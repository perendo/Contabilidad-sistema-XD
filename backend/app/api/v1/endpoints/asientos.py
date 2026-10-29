import logging
import re
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, solo_tesorero_o_admin, usuario_actual
from app.core.config import BASE_DIR, settings
from app.models.asiento import Apunte, Asiento, DocumentoAdjunto, TipoApunte
from app.models.usuario import Usuario
from app.schemas.asiento import AsientoCreate, AsientoRead, DocumentoRead

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=AsientoRead, status_code=status.HTTP_201_CREATED)
def crear_asiento(
    asiento_in: AsientoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(solo_tesorero_o_admin),
):

    # Obtener siguiente número de asiento por entidad+ejercicio
    max_num = (
        db.query(func.max(Asiento.numero_asiento))
        .filter(Asiento.entidad_id == asiento_in.entidad_id, Asiento.ejercicio_id == asiento_in.ejercicio_id)
        .scalar()
        or 0
    )
    nuevo_numero = max_num + 1

    db_asiento = Asiento(
        entidad_id=asiento_in.entidad_id,
        ejercicio_id=asiento_in.ejercicio_id,
        numero_asiento=nuevo_numero,
        fecha=asiento_in.fecha,
        concepto=asiento_in.concepto,
        descripcion=asiento_in.descripcion,
        registrado_por_id=usuario.id,
    )

    db.add(db_asiento)
    db.flush()

    for apunte_in in asiento_in.apuntes:
        db_apunte = Apunte(
            asiento_id=db_asiento.id,
            cuenta_id=apunte_in.cuenta_id,
            tipo=apunte_in.tipo,
            importe=apunte_in.importe,
        )
        db.add(db_apunte)

    db.commit()
    db.refresh(db_asiento)
    return db_asiento


MAX_ARCHIVOS = 20
LIMITE_TAMANO = 10 * 1024 * 1024
LIMITE_TOTAL = 50 * 1024 * 1024
MAX_CLAVE_IDEMPOTENCIA = 128
MAX_NOMBRE_ARCHIVO = 255
DIRECTORIO_LEGADO = BASE_DIR / "documentos"
FIRMAS = (
    (b"%PDF-", "application/pdf", ".pdf"),
    (b"\xff\xd8\xff", "image/jpeg", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", "image/png", ".png"),
)


def _nombre_carpeta(valor: str, entidad_id: UUID) -> str:
    """Nombre de carpeta seguro a partir del CIF, con respaldo si queda vacío."""
    limpio = "".join(caracter for caracter in valor if caracter.isalnum() or caracter in "-_")
    return limpio or f"entidad-{entidad_id}"


def _dentro_de(base: Path, destino: Path) -> bool:
    return destino == base or destino.is_relative_to(base)


def _directorio_documentos(asiento: Asiento) -> Path:
    base = settings.DIRECTORIO_DATOS.resolve()
    directorio = (
        base / _nombre_carpeta(asiento.entidad.cif, asiento.entidad_id) / str(asiento.ejercicio.anio)
    ).resolve()
    if not _dentro_de(base, directorio):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo determinar la carpeta del documento",
        )
    return directorio


def _resolver_documento(ruta: str) -> Path:
    """Resuelve la ruta guardada sin permitir que escape de los directorios de datos."""
    base = settings.DIRECTORIO_DATOS.resolve()
    normalizada = ruta.replace("\\", "/")
    candidata = Path(normalizada)
    if candidata.is_absolute():
        destino = candidata.resolve()
        legado = DIRECTORIO_LEGADO.resolve()
        if not (_dentro_de(base, destino) or _dentro_de(legado, destino)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
        return destino

    partes = [parte for parte in normalizada.split("/") if parte not in ("", ".")]
    destino = base.joinpath(*partes).resolve()
    if not _dentro_de(base, destino):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    return destino


def _nombre_archivo(archivo: UploadFile, por_defecto: str) -> str:
    nombre = re.split(r"[\\/]", archivo.filename or "")[-1]
    nombre = "".join(caracter for caracter in nombre if caracter.isprintable()).strip()
    return nombre[:MAX_NOMBRE_ARCHIVO] or por_defecto


def _leer_documento(archivo: UploadFile) -> tuple[bytes, str, str]:
    """Lee un documento y devuelve su contenido, tipo real y extensión."""
    if archivo.size is not None and archivo.size > LIMITE_TAMANO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cada archivo puede ocupar como máximo 10 MB",
        )

    contenido = archivo.file.read(LIMITE_TAMANO + 1)
    if not contenido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo está vacío")
    if len(contenido) > LIMITE_TAMANO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cada archivo puede ocupar como máximo 10 MB",
        )

    for firma, tipo, extension in FIRMAS:
        if contenido.startswith(firma):
            return contenido, tipo, extension

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Solo se admiten archivos PDF, JPG o PNG",
    )


def _borrar_archivos(rutas: list[Path], directorio: Path) -> None:
    for ruta in rutas:
        ruta.unlink(missing_ok=True)
    try:
        directorio.rmdir()
    except OSError:
        pass


def _documentos_con_clave(db: Session, asiento_id: UUID, clave: str) -> list[DocumentoAdjunto]:
    return (
        db.query(DocumentoAdjunto)
        .filter(
            DocumentoAdjunto.asiento_id == asiento_id,
            DocumentoAdjunto.clave_idempotencia == clave,
        )
        .order_by(DocumentoAdjunto.creado_en, DocumentoAdjunto.id)
        .all()
    )


@router.post(
    "/{asiento_id}/documentos",
    response_model=list[DocumentoRead],
    status_code=status.HTTP_201_CREATED,
)
def subir_documentos(
    asiento_id: UUID,
    archivos: list[UploadFile] = File(...),
    clave_idempotencia: str | None = Form(None, max_length=MAX_CLAVE_IDEMPOTENCIA),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(solo_tesorero_o_admin),
):
    asiento = db.query(Asiento).filter(Asiento.id == asiento_id).first()
    if not asiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asiento no encontrado")

    if len(archivos) > MAX_ARCHIVOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pueden adjuntar más de {MAX_ARCHIVOS} documentos a la vez",
        )
    if sum(archivo.size or 0 for archivo in archivos) > LIMITE_TOTAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El conjunto de documentos supera los 50 MB",
        )
    if clave_idempotencia and len(archivos) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La clave de idempotencia solo admite un archivo por petición",
        )

    # Se valida el contenido antes de mirar la clave: un reintento con un archivo
    # inválido nunca devuelve un 201 con los documentos antiguos.
    leidos = [(archivo, *_leer_documento(archivo)) for archivo in archivos]
    if sum(len(contenido) for _, contenido, _, _ in leidos) > LIMITE_TOTAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El conjunto de documentos supera los 50 MB",
        )

    if clave_idempotencia:
        existentes = _documentos_con_clave(db, asiento.id, clave_idempotencia)
        if existentes:
            return existentes

    directorio = _directorio_documentos(asiento)
    escritos: list[Path] = []
    documentos: list[DocumentoAdjunto] = []
    try:
        directorio.mkdir(parents=True, exist_ok=True)
        for archivo, contenido, tipo, extension in leidos:
            destino = directorio / f"{uuid4().hex}{extension}"
            escritos.append(destino)
            destino.write_bytes(contenido)
            documento = DocumentoAdjunto(
                asiento_id=asiento.id,
                nombre=_nombre_archivo(archivo, destino.name),
                tipo_contenido=tipo,
                tamano=len(contenido),
                ruta=destino.relative_to(settings.DIRECTORIO_DATOS.resolve()).as_posix(),
                clave_idempotencia=clave_idempotencia,
                subido_por_id=usuario.id,
            )
            db.add(documento)
            documentos.append(documento)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        _borrar_archivos(escritos, directorio)
        if clave_idempotencia:
            existentes = _documentos_con_clave(db, asiento.id, clave_idempotencia)
            if existentes:
                return existentes
        logger.exception("Conflicto al guardar documentos del asiento %s", asiento.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo completar la subida; inténtalo de nuevo",
        ) from error
    except HTTPException:
        db.rollback()
        _borrar_archivos(escritos, directorio)
        raise
    except Exception as error:
        db.rollback()
        _borrar_archivos(escritos, directorio)
        logger.exception("No se pudieron guardar los documentos del asiento %s", asiento.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudieron guardar los documentos",
        ) from error

    for documento in documentos:
        db.refresh(documento)
    return documentos


@router.get("/{asiento_id}/documentos/{documento_id}/descarga")
def descargar_documento(
    asiento_id: UUID,
    documento_id: UUID,
    db: Session = Depends(get_db),
):
    documento = (
        db.query(DocumentoAdjunto)
        .filter(
            DocumentoAdjunto.id == documento_id,
            DocumentoAdjunto.asiento_id == asiento_id,
        )
        .first()
    )
    if not documento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    ruta = _resolver_documento(documento.ruta)
    if not ruta.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    return FileResponse(
        ruta,
        media_type=documento.tipo_contenido,
        filename=documento.nombre,
    )


@router.get("/", response_model=list[AsientoRead])
def listar_asientos(entidad_id: UUID, ejercicio_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    asientos = (
        db.query(Asiento)
        .options(selectinload(Asiento.apuntes), selectinload(Asiento.documentos))
        .filter(Asiento.entidad_id == entidad_id, Asiento.ejercicio_id == ejercicio_id)
        .order_by(Asiento.fecha.desc(), Asiento.numero_asiento.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return asientos



@router.get("/{asiento_id}", response_model=AsientoRead)
def obtener_asiento(asiento_id: str, db: Session = Depends(get_db)):
    asiento = (
        db.query(Asiento)
        .options(selectinload(Asiento.apuntes), selectinload(Asiento.documentos))
        .filter(Asiento.id == asiento_id)
        .first()
    )
    if not asiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asiento no encontrado")
    return asiento
