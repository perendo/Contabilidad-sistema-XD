from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.v1.api import api_router
from app.core.config import CONTRASENA_ADMIN_DE_FABRICA, settings
from app.db.seed import sembrar_datos_iniciales
from app.db.session import SessionLocal

LIMITE_CUERPO_DOCUMENTOS = 55 * 1024 * 1024


def preparar_datos_iniciales() -> None:
    """Deja la base lista para usarse: roles fijos y administrador inicial."""
    if not settings.USE_SQLITE and settings.ADMIN_INICIAL_PASSWORD == CONTRASENA_ADMIN_DE_FABRICA:
        raise RuntimeError(
            "El administrador inicial sigue con la contraseña de fábrica. "
            "Define ADMIN_INICIAL_PASSWORD antes de arrancar contra PostgreSQL."
        )

    db = SessionLocal()
    try:
        sembrar_datos_iniciales(db)
    except OperationalError as error:
        raise RuntimeError(
            f"La base de datos no está preparada ({error}). "
            "Ejecuta `alembic upgrade head` y vuelve a arrancar."
        ) from error
    finally:
        db.close()


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    preparar_datos_iniciales()
    yield


app = FastAPI(
    title="Sistema Contable ONG - PGC España",
    description="Sistema contable con partida doble para ONG conforme al PGC español",
    version="0.1.0",
    lifespan=ciclo_de_vida,
)


@app.middleware("http")
async def limitar_cuerpo_de_documentos(request: Request, call_next):
    """Rechaza subidas enormes antes de que se vuelque el multipart a disco."""
    if request.url.path.endswith("/documentos"):
        longitud = request.headers.get("content-length")
        if longitud and longitud.isdigit() and int(longitud) > LIMITE_CUERPO_DOCUMENTOS:
            return JSONResponse(
                status_code=413,
                content={"detail": "La subida supera el tamaño máximo permitido"},
            )
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health():
    return {"estado": "ok"}
