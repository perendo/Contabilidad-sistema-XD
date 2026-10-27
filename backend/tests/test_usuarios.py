from app.models.usuario import Rol, RolEnum
from app.core.security import verificar_password


def test_solo_administrador_puede_crear_usuario(client, crear_usuario, db):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    rol_admin = db.query(Rol).filter(Rol.nombre == RolEnum.ADMINISTRADOR).first()
    if rol_admin is None:
        rol_admin = Rol(nombre=RolEnum.ADMINISTRADOR, descripcion=RolEnum.ADMINISTRADOR.value)
        db.add(rol_admin)
        db.commit()
        db.refresh(rol_admin)
    respuesta = client.post(
        "/api/v1/usuarios",
        json={
            "email": "nuevo@rendo.com",
            "nombre_completo": "Nuevo Usuario",
            "password": "ClaveSegura123",
            "rol_id": str(rol_admin.id),
        },
        headers=headers,
    )
    assert respuesta.status_code == 403


def test_crear_usuario_guarda_contraseña_cifrada_y_permite_login(client, cliente_admin, db):
    rol_admin = db.query(Rol).filter(Rol.nombre == RolEnum.ADMINISTRADOR).first()
    respuesta = client.post(
        "/api/v1/usuarios",
        json={
            "email": "nuevo@rendo.com",
            "nombre_completo": "Nuevo Usuario",
            "password": "ClaveSegura123",
            "rol_id": str(rol_admin.id),
        },
        headers=cliente_admin.headers,
    )
    assert respuesta.status_code == 201

    from app.models.usuario import Usuario

    usuario = db.query(Usuario).filter(Usuario.email == "nuevo@rendo.com").first()
    assert usuario is not None
    assert usuario.hashed_password != "ClaveSegura123"
    assert verificar_password("ClaveSegura123", usuario.hashed_password)

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "nuevo@rendo.com", "password": "ClaveSegura123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_solo_administrador_puede_listar_usuarios(client, crear_usuario):
    crear_usuario(email="lectura@rendo.com", rol=RolEnum.SOLO_LECTURA)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "lectura@rendo.com", "password": "Admin67@"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    respuesta = client.get("/api/v1/usuarios", headers=headers)
    assert respuesta.status_code == 403


def test_listar_usuarios_muestra_nombre_email_rol_y_activo(client, cliente_admin, crear_usuario):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    respuesta = client.get("/api/v1/usuarios", headers=cliente_admin.headers)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert isinstance(datos, list)
    emails = {u["email"] for u in datos}
    assert "tesorero@rendo.com" in emails
    for u in datos:
        if u["email"] == "tesorero@rendo.com":
            assert u["nombre_completo"]
            assert u["email"] == "tesorero@rendo.com"
            assert u["rol"]["nombre"] == "tesorero"
            assert "activo" in u
            break
    else:
        assert False, "No se encontró el usuario tesorero"
