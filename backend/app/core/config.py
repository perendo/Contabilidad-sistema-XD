import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

CONTRASENA_ADMIN_DE_FABRICA = "Admin67@"
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "Sistema Contable ONG"
    API_V1_STR: str = "/api/v1"

    POSTGRES_USER: str = "contabilidad"
    POSTGRES_PASSWORD: str = "contabilidad"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "contabilidad"

    SECRET_KEY: str = "cambiar-esta-clave-en-produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    USE_SQLITE: bool = True

    # Administrador que se crea solo en el primer arranque, si no existe.
    # Valores de desarrollo: con PostgreSQL el arranque se niega a usar la
    # contraseña de fábrica.
    ADMIN_INICIAL_EMAIL: str = "admin@ong.org"
    ADMIN_INICIAL_PASSWORD: str = CONTRASENA_ADMIN_DE_FABRICA

    # Raíz donde se guardan los documentos adjuntos, organizados por entidad y
    # ejercicio. En base de datos se guarda la ruta relativa a este directorio.
    DIRECTORIO_DATOS: Path = BASE_DIR / "data"

    @property
    def DATABASE_URL(self) -> str:
        if self.USE_SQLITE:
            return "sqlite:///./contabilidad.db"
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()

