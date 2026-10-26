import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.ejercicio import EjercicioRead


class EntidadCreate(BaseModel):
    cif: str
    nombre: str
    anio: int


class EntidadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cif: str
    nombre: str
    activa: bool
    creada_en: datetime
    ejercicios: list[EjercicioRead]
