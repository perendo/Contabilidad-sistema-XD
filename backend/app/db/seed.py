"""Datos que el sistema necesita para poder usarse desde el primer arranque."""

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.pgc import CUENTAS_BASE_PGC
from app.models.cuenta import Cuenta
from app.models.usuario import Rol, RolEnum, Usuario

logger = logging.getLogger(__name__)


def sembrar_cuentas_base(db: Session) -> None:
    """Añade al cuadro base las cuentas del PGC que todavía no existan."""

    existentes = {
        cuenta.codigo: cuenta
        for cuenta in db.query(Cuenta).filter(Cuenta.entidad_id.is_(None)).all()
    }

    for codigo, nombre in CUENTAS_BASE_PGC.items():
        cuenta = existentes.get(codigo)
        if cuenta is None:
            db.add(
                Cuenta(
                    entidad_id=None,
                    codigo=codigo,
                    nombre=nombre,
                    grupo=codigo[0],
                )
            )
        elif cuenta.nombre != nombre:
            # El catálogo del PGC es la referencia: corrige el nombre sin tocar
            # la descripción ni el estado de la cuenta.
            cuenta.nombre = nombre

    db.flush()


def sembrar_datos_iniciales(db: Session) -> None:
    """Crea los roles fijos y el administrador inicial si todavía no existen."""

    for rol_enum in RolEnum:
        if db.query(Rol).filter(Rol.nombre == rol_enum).first() is None:
            db.add(Rol(nombre=rol_enum, descripcion=rol_enum.value))

    db.flush()

    existente = db.query(Usuario).filter(Usuario.email == settings.ADMIN_INICIAL_EMAIL).first()

    if existente is None:
        rol_admin = db.query(Rol).filter(Rol.nombre == RolEnum.ADMINISTRADOR).one()
        db.add(
            Usuario(
                email=settings.ADMIN_INICIAL_EMAIL,
                nombre_completo="Administración",
                hashed_password=hash_password(settings.ADMIN_INICIAL_PASSWORD),
                rol_id=rol_admin.id,
            )
        )
        logger.warning(
            "Creado el administrador inicial %s con la contraseña configurada. "
            "Cámbiala antes de usar el sistema de verdad.",
            settings.ADMIN_INICIAL_EMAIL,
        )
    elif existente.rol.nombre != RolEnum.ADMINISTRADOR:
        logger.warning(
            "Ya existe un usuario con el email %s y no es administrador: "
            "no se ha creado el administrador inicial.",
            settings.ADMIN_INICIAL_EMAIL,
        )

    sembrar_cuentas_base(db)
    db.commit()
