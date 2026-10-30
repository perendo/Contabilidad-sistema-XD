import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TipoApunte(str, enum.Enum):
    DEBE = "debe"
    HABER = "haber"


class EstadoAsiento(str, enum.Enum):
    BORRADOR = "borrador"
    REGISTRADO = "registrado"


class Asiento(Base):
    __tablename__ = "asientos"
    __table_args__ = (
        UniqueConstraint("entidad_id", "ejercicio_id", "numero_asiento", name="uq_asientos_entidad_ejercicio_numero"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False)
    ejercicio_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ejercicios.id"), nullable=False)
    numero_asiento: Mapped[int] = mapped_column(nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    concepto: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    estado: Mapped[EstadoAsiento] = mapped_column(
        Enum(EstadoAsiento), nullable=False, default=EstadoAsiento.REGISTRADO
    )
    registrado_por_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modificado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entidad: Mapped["Entidad"] = relationship("Entidad", back_populates="asientos")
    ejercicio: Mapped["Ejercicio"] = relationship("Ejercicio", back_populates="asientos")
    apuntes: Mapped[list["Apunte"]] = relationship("Apunte", back_populates="asiento", cascade="all, delete-orphan")
    documentos: Mapped[list["DocumentoAdjunto"]] = relationship(
        "DocumentoAdjunto",
        back_populates="asiento",
        cascade="all, delete-orphan",
        order_by=lambda: [DocumentoAdjunto.creado_en, DocumentoAdjunto.id],
    )
    registrado_por: Mapped["Usuario"] = relationship("Usuario")



class Apunte(Base):
    __tablename__ = "apuntes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asiento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("asientos.id"), nullable=False)
    cuenta_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cuentas.id"), nullable=False)
    tipo: Mapped[TipoApunte] = mapped_column(Enum(TipoApunte), nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), nullable=False)

    asiento: Mapped[Asiento] = relationship("Asiento", back_populates="apuntes")
    cuenta: Mapped["Cuenta"] = relationship("Cuenta", back_populates="apuntes")


class DocumentoAdjunto(Base):
    __tablename__ = "documentos_adjuntos"
    __table_args__ = (
        UniqueConstraint("asiento_id", "clave_idempotencia", name="uq_documentos_asiento_clave"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asiento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asientos.id"), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    tipo_contenido: Mapped[str] = mapped_column(String, nullable=False)
    tamano: Mapped[int] = mapped_column(nullable=False)
    ruta: Mapped[str] = mapped_column(String, nullable=False)
    clave_idempotencia: Mapped[str | None] = mapped_column(String, nullable=True)
    subido_por_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    asiento: Mapped[Asiento] = relationship("Asiento", back_populates="documentos")
