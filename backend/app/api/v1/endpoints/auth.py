from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, usuario_actual
from app.core.security import crear_token_acceso, verificar_password
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenRead
from app.schemas.usuario import UsuarioRead

router = APIRouter()


@router.post("/login", response_model=TokenRead)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if usuario is None or not verificar_password(datos.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenRead(access_token=crear_token_acceso(usuario.email))


@router.get("/me", response_model=UsuarioRead)
def obtener_usuario_actual(usuario: Usuario = Depends(usuario_actual)):
    return usuario
