from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.entidad import Entidad
from app.models.ejercicio import Ejercicio
from app.schemas.entidad import EntidadCreate, EntidadRead
from app.schemas.ejercicio import EjercicioCreate, EjercicioRead

router = APIRouter()


@router.post("", response_model=EntidadRead, status_code=status.HTTP_201_CREATED)
def crear_entidad(entidad_in: EntidadCreate, db: Session = Depends(get_db)):
    existe = db.query(Entidad).filter(Entidad.cif == entidad_in.cif).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una entidad con ese CIF")

    db_entidad = Entidad(cif=entidad_in.cif, nombre=entidad_in.nombre)
    db.add(db_entidad)
    db.flush()
    db.add(
        Ejercicio(
            entidad_id=db_entidad.id,
            anio=entidad_in.anio,
            fecha_inicio=date(entidad_in.anio, 1, 1),
            fecha_fin=date(entidad_in.anio, 12, 31),
        )
    )
    db.commit()
    db.refresh(db_entidad)
    return db_entidad


@router.get("", response_model=list[EntidadRead])
def listar_entidades(db: Session = Depends(get_db)):
    entidades = db.query(Entidad).filter(Entidad.activa == True).order_by(Entidad.nombre).all()
    return entidades


@router.get("/{entidad_id}", response_model=EntidadRead)
def obtener_entidad(entidad_id: str, db: Session = Depends(get_db)):
    entidad = db.query(Entidad).filter(Entidad.id == entidad_id).first()
    if not entidad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entidad no encontrada")
    return entidad


@router.post("/{entidad_id}/ejercicios", response_model=EjercicioRead, status_code=status.HTTP_201_CREATED)
def crear_ejercicio(entidad_id: str, ejercicio_in: EjercicioCreate, db: Session = Depends(get_db)):
    entidad = db.query(Entidad).filter(Entidad.id == entidad_id).first()
    if not entidad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entidad no encontrada")

    # Validar que no exista ya un ejercicio para ese año
    existe = db.query(Ejercicio).filter(Ejercicio.entidad_id == entidad_id, Ejercicio.anio == ejercicio_in.anio).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un ejercicio para ese año en esta entidad")

    db_ejercicio = Ejercicio(entidad_id=entidad_id, **ejercicio_in.model_dump(exclude={"entidad_id"}))
    db.add(db_ejercicio)
    db.commit()
    db.refresh(db_ejercicio)
    return db_ejercicio


@router.get("/{entidad_id}/ejercicios", response_model=list[EjercicioRead])
def listar_ejercicios(entidad_id: str, db: Session = Depends(get_db)):
    ejercicios = db.query(Ejercicio).filter(Ejercicio.entidad_id == entidad_id).order_by(Ejercicio.anio.desc()).all()
    return ejercicios
