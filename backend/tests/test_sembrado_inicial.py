import pytest

from app.core.config import CONTRASENA_ADMIN_DE_FABRICA, settings
from app.db.seed import sembrar_datos_iniciales
from app.main import preparar_datos_iniciales
from app.models.cuenta import Cuenta


def test_el_administrador_inicial_puede_entrar_tras_sembrar(db, client):
    sembrar_datos_iniciales(db)

    login = client.post(
        "/api/v1/auth/login",
        json={"email": settings.ADMIN_INICIAL_EMAIL, "password": settings.ADMIN_INICIAL_PASSWORD},
    )

    assert login.status_code == 200
    token = login.json()["access_token"]

    yo = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert yo.status_code == 200
    assert yo.json()["email"] == settings.ADMIN_INICIAL_EMAIL
    assert yo.json()["rol"]["nombre"] == "administrador"


def test_sembrar_dos_veces_no_duplica_roles_ni_usuarios(fabrica_sesiones, client):
    # Dos arranques seguidos de la aplicación, cada uno con su propia sesión.
    for _ in range(2):
        sesion = fabrica_sesiones()
        try:
            sembrar_datos_iniciales(sesion)
        finally:
            sesion.close()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": settings.ADMIN_INICIAL_EMAIL, "password": settings.ADMIN_INICIAL_PASSWORD},
    )
    assert login.status_code == 200
    cabeceras = {"Authorization": f"Bearer {login.json()['access_token']}"}

    usuarios = client.get("/api/v1/usuarios", headers=cabeceras)
    roles = client.get("/api/v1/usuarios/roles", headers=cabeceras)

    assert len(usuarios.json()) == 1
    assert sorted(rol["nombre"] for rol in roles.json()) == ["administrador", "solo_lectura", "tesorero"]


def test_con_postgres_y_contrasena_de_fabrica_el_arranque_se_niega(monkeypatch):
    monkeypatch.setattr(settings, "USE_SQLITE", False)
    monkeypatch.setattr(settings, "ADMIN_INICIAL_PASSWORD", CONTRASENA_ADMIN_DE_FABRICA)

    with pytest.raises(RuntimeError, match="contraseña de fábrica"):
        preparar_datos_iniciales()


def test_el_arranque_siembra_el_cuadro_base_una_sola_vez(fabrica_sesiones):
    def sembrar_y_leer():
        sesion = fabrica_sesiones()
        try:
            sembrar_datos_iniciales(sesion)
            return [
                (cuenta.codigo, cuenta.grupo)
                for cuenta in sesion.query(Cuenta).filter(Cuenta.entidad_id.is_(None)).all()
            ]
        finally:
            sesion.close()

    primera = sembrar_y_leer()
    segunda = sembrar_y_leer()

    codigos = {codigo for codigo, _ in primera}
    assert len(primera) == len(segunda)
    assert len(codigos) == len(primera)
    assert {"100", "200", "300", "400", "500", "600", "700", "800", "900"} <= codigos
    assert all(codigo[0] == grupo for codigo, grupo in primera)
