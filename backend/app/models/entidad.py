import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Entidad(Base):
    __tablename__ = "entidades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cif: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ejercicios: Mapped[list["Ejercicio"]] = relationship("Ejercicio", back_populates="entidad", cascade="all, delete-orphan")
    asientos: Mapped[list["Asiento"]] = relationship("Asiento", back_populates="entidad")
    cuentas: Mapped[list["Cuenta"]] = relationship("Cuenta", back_populates="entidad")
