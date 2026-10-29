from datetime import date
from uuid import uuid4

import pytest

from app.core.config import settings
from app.models.cuenta import Cuenta
from app.models.entidad import Entidad
from app.models.ejercicio import Ejercicio


@pytest.fixture(autouse=True)
def directorio_datos(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DIRECTORIO_DATOS", tmp_path)
    return tmp_path


def _contexto(db, cif="A11111111", nombre="Entidad1", anio=2026):
    entidad = Entidad(cif=cif, nombre=nombre, activa=True)
    db.add(entidad)
    db.flush()
    ejercicio = Ejercicio(
        entidad_id=entidad.id,
        anio=anio,
        fecha_inicio=date(anio, 1, 1),
        fecha_fin=date(anio, 12, 31),
    )
    db.add(ejercicio)
    debe = Cuenta(codigo="600", nombre="Compras", grupo="6", activa=True)
    haber = Cuenta(codigo="570", nombre="Caja", grupo="5", activa=True)
    db.add_all([debe, haber])
    db.commit()
    return entidad, ejercicio, debe, haber


def _alta_asiento(cliente, entidad, ejercicio, debe, haber, concepto="Compra de material"):
    respuesta = cliente.post(
        "/api/v1/asientos/",
        json={
            "entidad_id": str(entidad.id),
            "ejercicio_id": str(ejercicio.id),
            "fecha": "2026-01-15",
            "concepto": concepto,
            "apuntes": [
                {"cuenta_id": str(debe.id), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(haber.id), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _subir(cliente, asiento_id, archivos, clave=None):
    datos = {"clave_idempotencia": clave} if clave else None
    return cliente.post(
        f"/api/v1/asientos/{asiento_id}/documentos",
        files=archivos,
        data=datos,
    )


def _documentos(cliente, entidad, ejercicio):
    listado = cliente.get(
        "/api/v1/asientos/",
        params={"entidad_id": str(entidad.id), "ejercicio_id": str(ejercicio.id)},
    )
    assert listado.status_code == 200
    return listado.json()[0]["documentos"]


def test_adjuntar_dos_documentos_a_un_asiento_los_devuelve_en_el_listado(
    cliente_tesorero, db, tmp_path
):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [
            ("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf")),
            ("archivos", ("recibo.jpg", b"\xff\xd8\xff", "image/jpeg")),
        ],
    )

    assert subida.status_code == 201

    documentos = _documentos(cliente_tesorero, entidad, ejercicio)
    assert {documento["nombre"]: documento["tamano"] for documento in documentos} == {
        "factura.pdf": 8,
        "recibo.jpg": 3,
    }
    carpeta = tmp_path / "A11111111" / "2026"
    assert carpeta.is_dir()
    assert len(list(carpeta.iterdir())) == 2


def test_la_descarga_devuelve_el_archivo_con_su_nombre_y_contenido(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("factura.pdf", b"%PDF-1.4 factura", "application/pdf"))],
    )
    assert subida.status_code == 201
    documento_id = subida.json()[0]["id"]

    descarga = cliente_tesorero.get(
        f"/api/v1/asientos/{asiento_id}/documentos/{documento_id}/descarga"
    )

    assert descarga.status_code == 200
    assert descarga.content == b"%PDF-1.4 factura"
    assert "factura.pdf" in descarga.headers["content-disposition"]


def test_la_descarga_conserva_el_nombre_original_no_ascii(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("presupuesto año.pdf", b"%PDF-1.4 factura", "application/pdf"))],
    )
    assert subida.status_code == 201
    documento_id = subida.json()[0]["id"]

    descarga = cliente_tesorero.get(
        f"/api/v1/asientos/{asiento_id}/documentos/{documento_id}/descarga"
    )

    assert descarga.status_code == 200
    assert "filename*=utf-8''" in descarga.headers["content-disposition"].lower()


def test_la_descarga_devuelve_404_si_el_fichero_no_esta_en_disco(cliente_tesorero, db, tmp_path):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))],
    )
    documento_id = subida.json()[0]["id"]
    archivos = list(tmp_path.rglob("*.pdf"))
    assert len(archivos) == 1
    archivos[0].unlink()

    descarga = cliente_tesorero.get(
        f"/api/v1/asientos/{asiento_id}/documentos/{documento_id}/descarga"
    )

    assert descarga.status_code == 404
    assert descarga.json()["detail"] == "Documento no encontrado"


def test_se_rechaza_un_archivo_que_no_es_pdf_jpg_ni_png(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("notas.txt", b"hola", "text/plain"))],
    )

    assert subida.status_code == 400
    assert subida.json()["detail"] == "Solo se admiten archivos PDF, JPG o PNG"
    assert _documentos(cliente_tesorero, entidad, ejercicio) == []


def test_se_rechaza_un_archivo_cuyo_contenido_no_corresponde_al_tipo(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("falso.pdf", b"<html>no soy un pdf</html>", "application/pdf"))],
    )

    assert subida.status_code == 400
    assert subida.json()["detail"] == "Solo se admiten archivos PDF, JPG o PNG"
    assert _documentos(cliente_tesorero, entidad, ejercicio) == []


def test_se_rechaza_un_archivo_vacio(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("vacio.pdf", b"", "application/pdf"))],
    )

    assert subida.status_code == 400
    assert subida.json()["detail"] == "El archivo está vacío"


def test_se_rechaza_un_archivo_de_mas_de_10_mb(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)
    contenido = b"x" * (10 * 1024 * 1024 + 1)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("grande.pdf", contenido, "application/pdf"))],
    )

    assert subida.status_code == 400
    assert subida.json()["detail"] == "Cada archivo puede ocupar como máximo 10 MB"
    assert _documentos(cliente_tesorero, entidad, ejercicio) == []


def test_se_rechaza_un_lote_que_supera_el_limite_total(cliente_tesorero, db, monkeypatch):
    from app.api.v1.endpoints import asientos as endpoint_asientos

    monkeypatch.setattr(endpoint_asientos, "LIMITE_TOTAL", 5)
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [
            ("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf")),
            ("archivos", ("recibo.jpg", b"\xff\xd8\xff", "image/jpeg")),
        ],
    )

    assert subida.status_code == 400
    assert subida.json()["detail"] == "El conjunto de documentos supera los 50 MB"
    assert _documentos(cliente_tesorero, entidad, ejercicio) == []


def test_si_un_archivo_del_lote_no_es_valido_no_se_guarda_ninguno(
    cliente_tesorero, db, tmp_path
):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [
            ("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf")),
            ("archivos", ("notas.txt", b"hola", "text/plain")),
        ],
    )

    assert subida.status_code == 400
    assert _documentos(cliente_tesorero, entidad, ejercicio) == []
    assert list(tmp_path.rglob("*.*")) == []


def test_se_rechaza_mas_de_20_archivos_en_una_sola_subida(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)
    archivos = [
        ("archivos", (f"factura-{indice}.pdf", b"%PDF-1.4", "application/pdf"))
        for indice in range(21)
    ]

    subida = _subir(cliente_tesorero, asiento_id, archivos)

    assert subida.status_code == 400
    assert subida.json()["detail"] == "No se pueden adjuntar más de 20 documentos a la vez"


def test_solo_lectura_recibe_403_al_intentar_subir_un_documento(cliente_solo_lectura):
    subida = _subir(
        cliente_solo_lectura,
        uuid4(),
        [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))],
    )

    assert subida.status_code == 403


def test_administrador_puede_adjuntar_documentos(cliente_admin, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_admin, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_admin,
        asiento_id,
        [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))],
    )

    assert subida.status_code == 201


def test_subir_a_un_asiento_inexistente_devuelve_404(cliente_tesorero):
    subida = _subir(
        cliente_tesorero,
        uuid4(),
        [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))],
    )

    assert subida.status_code == 404


def test_adjuntar_a_un_asiento_que_ya_tiene_documentos_los_suma(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))],
    )
    _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("recibo.jpg", b"\xff\xd8\xff", "image/jpeg"))],
    )

    documentos = _documentos(cliente_tesorero, entidad, ejercicio)
    assert {documento["nombre"] for documento in documentos} == {"factura.pdf", "recibo.jpg"}


def test_un_cif_peligroso_no_saca_los_documentos_de_la_raiz(cliente_tesorero, db, tmp_path):
    from app.models.asiento import DocumentoAdjunto

    entidad, ejercicio, debe, haber = _contexto(db, cif="..")
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))],
    )

    assert subida.status_code == 201
    documento = db.query(DocumentoAdjunto).one()
    ruta = tmp_path / documento.ruta
    assert ruta.is_file()
    assert ruta.resolve().is_relative_to(tmp_path.resolve())
    assert ".." not in documento.ruta.split("/")
    assert documento.ruta.startswith(f"entidad-{entidad.id}/")


def test_no_se_puede_descargar_un_documento_de_otro_asiento(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_con_documento = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)
    otro_asiento = _alta_asiento(
        cliente_tesorero, entidad, ejercicio, debe, haber, concepto="Otro asiento"
    )

    subida = _subir(
        cliente_tesorero,
        asiento_con_documento,
        [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))],
    )
    documento_id = subida.json()[0]["id"]

    descarga = cliente_tesorero.get(
        f"/api/v1/asientos/{otro_asiento}/documentos/{documento_id}/descarga"
    )

    assert descarga.status_code == 404


def test_la_misma_clave_de_idempotencia_no_duplica_el_documento(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)
    archivo = [("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf"))]

    primera = _subir(cliente_tesorero, asiento_id, archivo, clave="envio-1")
    segunda = _subir(cliente_tesorero, asiento_id, archivo, clave="envio-1")

    assert primera.status_code == 201
    assert segunda.status_code == 201
    documentos = _documentos(cliente_tesorero, entidad, ejercicio)
    assert [documento["nombre"] for documento in documentos] == ["factura.pdf"]


def test_la_clave_de_idempotencia_admite_un_solo_archivo(cliente_tesorero, db):
    entidad, ejercicio, debe, haber = _contexto(db)
    asiento_id = _alta_asiento(cliente_tesorero, entidad, ejercicio, debe, haber)

    subida = _subir(
        cliente_tesorero,
        asiento_id,
        [
            ("archivos", ("factura.pdf", b"%PDF-1.4", "application/pdf")),
            ("archivos", ("recibo.jpg", b"\xff\xd8\xff", "image/jpeg")),
        ],
        clave="envio-1",
    )

    assert subida.status_code == 400
    assert subida.json()["detail"] == "La clave de idempotencia solo admite un archivo por petición"
