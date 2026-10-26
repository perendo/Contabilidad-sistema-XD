import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CuentaBase(BaseModel):
    codigo: str
    nombre: str
    grupo: str
    descripcion: str | None = None
    activa: bool = True


class CuentaCreate(CuentaBase):
    entidad_id: uuid.UUID


class CuentaRead(CuentaBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entidad_id: uuid.UUID
    creada_en: datetime

