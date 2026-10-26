from fastapi import APIRouter

from app.api.v1.endpoints import asientos, cuentas, entidades, usuarios

api_router = APIRouter()
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
api_router.include_router(entidades.router, prefix="/entidades", tags=["Entidades"])
api_router.include_router(cuentas.router, prefix="/cuentas", tags=["Cuentas"])
api_router.include_router(asientos.router, prefix="/asientos", tags=["Asientos"])


