from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.usuario import Rol, RolEnum, Usuario
from app.schemas.usuario import RolRead, UsuarioCreate, UsuarioRead

router = APIRouter()


@router.get("/roles", response_model=list[RolRead])
def listar_roles(db: Session = Depends(get_db)):
    roles = db.query(Rol).all()
    return roles


@router.post("/roles/seed", response_model=list[RolRead])
def seed_roles(db: Session = Depends(get_db)):
    roles_existentes = {r.nombre for r in db.query(Rol).all()}
    creados = []
    for rol_enum in RolEnum:
        if rol_enum not in roles_existentes:
            rol = Rol(nombre=rol_enum, descripcion=rol_enum.value)
            db.add(rol)
            creados.append(rol)
    db.commit()
    for r in creados:
        db.refresh(r)
    return db.query(Rol).all()


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.query(Usuario).filter(Usuario.email == usuario_in.email).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un usuario con ese email")

    # Por simplicidad guardamos la contraseña tal como viene (se reemplazará con hash)
    db_usuario = Usuario(
        email=usuario_in.email,
        nombre_completo=usuario_in.nombre_completo,
        hashed_password=usuario_in.password,
        rol_id=usuario_in.rol_id,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios
