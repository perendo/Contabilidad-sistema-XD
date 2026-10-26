import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TipoApunte(str, Enum):
    DEBE = "debe"
    HABER = "haber"


class ApunteCreate(BaseModel):
    cuenta_id: uuid.UUID
    tipo: TipoApunte
    importe: Decimal = Field(gt=0, decimal_places=2)


class ApunteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cuenta_id: uuid.UUID
    tipo: TipoApunte
    importe: Decimal


class AsientoCreate(BaseModel):
    entidad_id: uuid.UUID
    ejercicio_id: uuid.UUID
    fecha: date
    concepto: str
    descripcion: str | None = None
    apuntes: list[ApunteCreate]

    @model_validator(mode="after")
    def validar_partida_doble(self):
        if not self.apuntes or len(self.apuntes) < 2:
            raise ValueError("Un asiento debe tener al menos dos apuntes")

        total_debe = sum((a.importe for a in self.apuntes if a.tipo == TipoApunte.DEBE), Decimal("0"))
        total_haber = sum((a.importe for a in self.apuntes if a.tipo == TipoApunte.HABER), Decimal("0"))

        if total_debe != total_haber:
            raise ValueError("El asiento no está cuadrado. Debe y Haber deben ser iguales")
        if total_debe <= 0:
            raise ValueError("Los importes deben ser superiores a 0")

        return self


class AsientoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entidad_id: uuid.UUID
    ejercicio_id: uuid.UUID
    numero_asiento: int
    fecha: date
    concepto: str
    descripcion: str | None = None
    registrado_por_id: uuid.UUID
    creado_en: datetime
    modificado_en: datetime
    apuntes: list[ApunteRead]

