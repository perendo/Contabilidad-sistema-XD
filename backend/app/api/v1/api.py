from fastapi import APIRouter, Depends

from app.api.deps import usuario_actual
from app.api.v1.endpoints import asientos, auth, cuentas, entidades, usuarios

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

protegido = [Depends(usuario_actual)]
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"], dependencies=protegido)
api_router.include_router(entidades.router, prefix="/entidades", tags=["Entidades"], dependencies=protegido)
api_router.include_router(cuentas.router, prefix="/cuentas", tags=["Cuentas"], dependencies=protegido)
api_router.include_router(asientos.router, prefix="/asientos", tags=["Asientos"], dependencies=protegido)
