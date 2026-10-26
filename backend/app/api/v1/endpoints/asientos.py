from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.asiento import Apunte, Asiento, TipoApunte
from app.models.usuario import Usuario
from app.schemas.asiento import AsientoCreate, AsientoRead

router = APIRouter()


@router.post("/", response_model=AsientoRead, status_code=status.HTTP_201_CREATED)
def crear_asiento(asiento_in: AsientoCreate, db: Session = Depends(get_db)):
    # Por ahora usamos un usuario de prueba (se reemplazará con auth + roles)
    usuario = db.query(Usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay usuarios en la base de datos. Crea un usuario primero.",
        )

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


@router.get("/", response_model=list[AsientoRead])
def listar_asientos(entidad_id: str, ejercicio_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    asientos = (
        db.query(Asiento)
        .filter(Asiento.entidad_id == entidad_id, Asiento.ejercicio_id == ejercicio_id)
        .order_by(Asiento.fecha.desc(), Asiento.numero_asiento.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return asientos



@router.get("/{asiento_id}", response_model=AsientoRead)
def obtener_asiento(asiento_id: str, db: Session = Depends(get_db)):
    asiento = db.query(Asiento).filter(Asiento.id == asiento_id).first()
    if not asiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asiento no encontrado")
    return asiento
