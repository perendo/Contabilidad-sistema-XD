import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.models.usuario import Rol, RolEnum, Usuario

# bcrypt de "Admin67@" con 4 rondas. Hash fijo a propósito: el test de login no
# debe depender del mismo código que hashea en producción.
HASH_ADMIN = "$2b$04$4fgz/h5p4iDzKScDJRg2fOgjo9CwhOL.G9WS5TShfHPUhWljbxmzu"


@pytest.fixture
def fabrica_sesiones():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield sessionmaker(autocommit=False, autoflush=False, bind=engine)
    engine.dispose()


@pytest.fixture
def db(fabrica_sesiones):
    session = fabrica_sesiones()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(fabrica_sesiones):
    def get_db_override():
        session = fabrica_sesiones()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_db_override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def crear_usuario(db):
    def _crear(email: str = "admin@rendo.com", rol: RolEnum = RolEnum.ADMINISTRADOR) -> Usuario:
        rol_db = db.query(Rol).filter(Rol.nombre == rol).first()
        if rol_db is None:
            rol_db = Rol(nombre=rol, descripcion=rol.value)
            db.add(rol_db)
            db.flush()
        usuario = Usuario(
            email=email,
            nombre_completo=email.split("@")[0],
            hashed_password=HASH_ADMIN,
            rol_id=rol_db.id,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    return _crear


def _cliente_con_rol(client, crear_usuario, email, rol=RolEnum.ADMINISTRADOR):
    crear_usuario(email=email, rol=rol)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Admin67@"},
    )
    client.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
    return client


@pytest.fixture
def cliente_admin(client, crear_usuario):
    return _cliente_con_rol(client, crear_usuario, "admin@rendo.com")


@pytest.fixture
def cliente_tesorero(client, crear_usuario):
    return _cliente_con_rol(client, crear_usuario, "tesorero@rendo.com", RolEnum.TESORERO)


@pytest.fixture
def cliente_solo_lectura(client, crear_usuario):
    return _cliente_con_rol(client, crear_usuario, "lectura@rendo.com", RolEnum.SOLO_LECTURA)
