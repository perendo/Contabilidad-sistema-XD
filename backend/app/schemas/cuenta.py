import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class CuentaBase(BaseModel):
    codigo: str
    nombre: str
    grupo: str
    descripcion: str | None = None
    activa: bool = True

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        codigo = v.strip()
        if not codigo:
            raise ValueError("El código de la cuenta es obligatorio")
        return codigo


class CuentaCreate(CuentaBase):
    entidad_id: uuid.UUID | None = None

    @field_validator("codigo")
    @classmethod
    def validar_codigo_base(cls, v: str) -> str:
        codigo = v.strip()
        if not codigo.isdigit():
            raise ValueError("El código de la cuenta base debe ser numérico")
        if len(codigo) > 8:
            raise ValueError("El código de la cuenta base no puede tener más de 8 dígitos")
        return codigo


class CuentaRead(CuentaBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entidad_id: uuid.UUID | None
    creada_en: datetime

