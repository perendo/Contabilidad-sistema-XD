from app.models.usuario import RolEnum


def test_tesorero_puede_crear_cuenta_base_con_codigo_numerico_hasta_8_digitos_y_aparece_en_base(
    client, crear_usuario, db
):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "12345678",
            "nombre": "Cuenta base de prueba",
            "grupo": "1",
            "descripcion": None,
            "activa": True,
            "entidad_id": None,
        },
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["entidad_id"] is None
    assert datos["codigo"] == "12345678"

    respuesta_base = client.get("/api/v1/cuentas/base")
    assert respuesta_base.status_code == 200
    codigos = [c["codigo"] for c in respuesta_base.json()]
    assert "12345678" in codigos


def test_administrador_puede_crear_cuenta_base_con_codigo_numerico_hasta_8_digitos_y_aparece_en_base(
    client, crear_usuario, db
):
    crear_usuario(email="admin2@rendo.com", rol=RolEnum.ADMINISTRADOR)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin2@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "76543210",
            "nombre": "Cuenta base admin",
            "grupo": "2",
            "descripcion": None,
            "activa": True,
            "entidad_id": None,
        },
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["entidad_id"] is None
    assert datos["codigo"] == "76543210"

    respuesta_base = client.get("/api/v1/cuentas/base")
    assert respuesta_base.status_code == 200
    codigos = [c["codigo"] for c in respuesta_base.json()]
    assert "76543210" in codigos


def test_crear_cuenta_base_con_codigo_ya_existente_devuelve_error_con_mensaje_adecuado(
    client, crear_usuario, db
):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta1 = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "123456",
            "nombre": "Cuenta base 1",
            "grupo": "1",
            "descripcion": None,
            "activa": True,
            "entidad_id": None,
        },
    )
    assert respuesta1.status_code == 201

    respuesta2 = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "123456",
            "nombre": "Cuenta base 2",
            "grupo": "1",
            "descripcion": None,
            "activa": True,
            "entidad_id": None,
        },
    )
    assert respuesta2.status_code == 400
    assert respuesta2.json()["detail"] == "Ya existe una cuenta base con ese código"


def test_solo_lectura_no_puede_crear_cuenta_base_devuelve_403(
    client, crear_usuario, db
):
    crear_usuario(email="lectura@rendo.com", rol=RolEnum.SOLO_LECTURA)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "lectura@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "1234567",
            "nombre": "Cuenta base lectura",
            "grupo": "1",
            "descripcion": None,
            "activa": True,
            "entidad_id": None,
        },
    )

    assert respuesta.status_code == 403


def test_crear_cuenta_base_con_mas_de_8_digitos_devuelve_error(
    client, crear_usuario, db
):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "123456789",
            "nombre": "Cuenta base larga",
            "grupo": "1",
            "descripcion": None,
            "activa": True,
            "entidad_id": None,
        },
    )

    assert respuesta.status_code in (400, 422)


def test_crear_cuenta_base_con_codigo_no_numerico_devuelve_error(
    client, crear_usuario, db
):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "123A456",
            "nombre": "Cuenta base no numerica",
            "grupo": "1",
            "descripcion": None,
            "activa": True,
            "entidad_id": None,
        },
    )

    assert respuesta.status_code in (400, 422)


def test_crear_cuenta_por_entidad_sigue_permitiendo_codigo_numerico_hasta_8_digitos_y_es_unica_por_entidad(
    client, crear_usuario, db
):
    import uuid

    from app.models.entidad import Entidad

    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad1 = Entidad(cif="A11111111", nombre="Entidad1", activa=True)
    entidad2 = Entidad(cif="A22222222", nombre="Entidad2", activa=True)
    db.add_all([entidad1, entidad2])
    db.commit()
    db.refresh(entidad1)
    db.refresh(entidad2)

    respuesta1 = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "60000000",
            "nombre": "Cuenta entidad 1",
            "grupo": "6",
            "descripcion": None,
            "activa": True,
            "entidad_id": str(entidad1.id),
        },
    )
    assert respuesta1.status_code == 201

    respuesta2 = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "60000000",
            "nombre": "Cuenta entidad 2",
            "grupo": "6",
            "descripcion": None,
            "activa": True,
            "entidad_id": str(entidad2.id),
        },
    )
    assert respuesta2.status_code == 201
    assert respuesta2.json()["entidad_id"] == str(entidad2.id)

    respuesta_dup = client.post(
        "/api/v1/cuentas/",
        json={
            "codigo": "60000000",
            "nombre": "Cuenta entidad 1 duplicada",
            "grupo": "6",
            "descripcion": None,
            "activa": True,
            "entidad_id": str(entidad1.id),
        },
    )
    assert respuesta_dup.status_code == 400
    assert respuesta_dup.json()["detail"] == "Ya existe una cuenta con ese código"
