import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.ejercicio import EjercicioRead

PATRON_CIF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class EntidadCreate(BaseModel):
    cif: str = Field(min_length=1, max_length=32)
    nombre: str
    anio: int

    @field_validator("cif")
    @classmethod
    def validar_cif(cls, valor: str) -> str:
        """El CIF se usa como nombre de carpeta: sin barras ni puntos suspensivos."""
        limpio = valor.strip()
        if not PATRON_CIF.fullmatch(limpio):
            raise ValueError(
                "El CIF solo admite letras, números, puntos, guiones y guiones bajos, "
                "y debe empezar por letra o número"
            )
        return limpio


class EntidadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cif: str
    nombre: str
    activa: bool
    creada_en: datetime
    ejercicios: list[EjercicioRead]
