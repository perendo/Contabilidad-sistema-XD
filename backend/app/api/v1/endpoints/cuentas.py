from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, solo_tesorero_o_admin
from app.models.cuenta import Cuenta
from app.models.usuario import Usuario
from app.schemas.cuenta import CuentaCreate, CuentaRead

router = APIRouter()


@router.post("/", response_model=CuentaRead, status_code=status.HTTP_201_CREATED)
def crear_cuenta(cuenta_in: CuentaCreate, db: Session = Depends(get_db)):
    existe = (
        db.query(Cuenta)
        .filter(Cuenta.entidad_id == cuenta_in.entidad_id, Cuenta.codigo == cuenta_in.codigo)
        .first()
    )
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una cuenta con ese código")

    db_cuenta = Cuenta(**cuenta_in.model_dump())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


@router.get("/", response_model=list[CuentaRead])
def listar_cuentas(entidad_id: str, db: Session = Depends(get_db)):
    cuentas = db.query(Cuenta).filter(Cuenta.entidad_id == entidad_id, Cuenta.activa == True).order_by(Cuenta.codigo).all()
    return cuentas



@router.get("/base", response_model=list[CuentaRead])
def listar_cuentas_base(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(solo_tesorero_o_admin),
):
    """Cuadro de cuentas base compartido: cuentas sin entidad asignada."""

    return (
        db.query(Cuenta)
        .filter(Cuenta.entidad_id.is_(None), Cuenta.activa == True)
        .order_by(Cuenta.codigo)
        .all()
    )


@router.get("/{cuenta_id}", response_model=CuentaRead)
def obtener_cuenta(cuenta_id: str, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
    if not cuenta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")
    return cuenta
