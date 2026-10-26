import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class RolEnum(str, Enum):
    ADMINISTRADOR = "administrador"
    TESORERO = "tesorero"
    SOLO_LECTURA = "solo_lectura"


class RolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: RolEnum
    descripcion: str | None = None


class UsuarioBase(BaseModel):
    email: EmailStr
    nombre_completo: str


class UsuarioCreate(UsuarioBase):
    password: str
    rol_id: uuid.UUID


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    activo: bool
    creado_en: datetime
    rol: RolRead
