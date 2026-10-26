import pytest

ID_INEXISTENTE = "00000000-0000-0000-0000-000000000000"

ENDPOINTS_PROTEGIDOS = [
    ("GET", "/api/v1/auth/me"),
    ("GET", "/api/v1/usuarios"),
    ("POST", "/api/v1/usuarios"),
    ("GET", "/api/v1/usuarios/roles"),
    ("POST", "/api/v1/usuarios/roles/seed"),
    ("GET", "/api/v1/entidades"),
    ("POST", "/api/v1/entidades"),
    ("GET", f"/api/v1/entidades/{ID_INEXISTENTE}"),
    ("GET", f"/api/v1/entidades/{ID_INEXISTENTE}/ejercicios"),
    ("POST", f"/api/v1/entidades/{ID_INEXISTENTE}/ejercicios"),
    ("GET", f"/api/v1/cuentas?entidad_id={ID_INEXISTENTE}"),
    ("POST", "/api/v1/cuentas"),
    ("GET", f"/api/v1/cuentas/{ID_INEXISTENTE}"),
    ("GET", f"/api/v1/asientos?entidad_id={ID_INEXISTENTE}&ejercicio_id={ID_INEXISTENTE}"),
    ("POST", "/api/v1/asientos"),
    ("GET", f"/api/v1/asientos/{ID_INEXISTENTE}"),
]


@pytest.mark.parametrize("metodo, ruta", ENDPOINTS_PROTEGIDOS)
def test_sin_token_los_endpoints_protegidos_devuelven_401(client, metodo, ruta):
    respuesta = client.request(metodo, ruta)

    assert respuesta.status_code == 401
