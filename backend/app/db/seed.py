"""Datos que el sistema necesita para poder usarse desde el primer arranque."""

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.usuario import Rol, RolEnum, Usuario

logger = logging.getLogger(__name__)


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

    db.commit()
