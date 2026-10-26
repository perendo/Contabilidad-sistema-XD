import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator


class EjercicioBase(BaseModel):
    anio: int
    fecha_inicio: date
    fecha_fin: date
    cerrado: bool = False


class EjercicioCreate(EjercicioBase):
    entidad_id: uuid.UUID

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior o igual a la fecha de inicio")
        if self.fecha_inicio.year != self.anio or self.fecha_fin.year != self.anio:
            raise ValueError("Las fechas deben pertenecer al año del ejercicio")
        return self


class EjercicioRead(EjercicioBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entidad_id: uuid.UUID
    creado_en: datetime
