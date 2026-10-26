import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ejercicio(Base):
    __tablename__ = "ejercicios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False)
    anio: Mapped[int] = mapped_column("año", Integer, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    cerrado: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entidad: Mapped["Entidad"] = relationship("Entidad", back_populates="ejercicios")
    asientos: Mapped[list["Asiento"]] = relationship("Asiento", back_populates="ejercicio")
