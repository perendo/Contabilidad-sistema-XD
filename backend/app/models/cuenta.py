import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Cuenta(Base):
    __tablename__ = "cuentas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    grupo: Mapped[str] = mapped_column(String, nullable=False)  # Grupo del PGC
    descripcion: Mapped[str] = mapped_column(String, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entidad: Mapped["Entidad"] = relationship("Entidad", back_populates="cuentas")
    apuntes: Mapped[list["Apunte"]] = relationship("Apunte", back_populates="cuenta")

