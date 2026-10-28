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


def test_listar_cuentas_para_entidad_incluye_cuentas_base_compartidas(
    client, crear_usuario, db
):
    import uuid

    from app.models.cuenta import Cuenta
    from app.models.entidad import Entidad

    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad = Entidad(cif="A11111111", nombre="Entidad1", activa=True)
    db.add(entidad)
    db.commit()
    db.refresh(entidad)

    cuenta_base = Cuenta(
        codigo="43000000",
        nombre="Cuenta base compartida",
        grupo="4",
        entidad_id=None,
        activa=True,
    )
    cuenta_entidad = Cuenta(
        codigo="60000001",
        nombre="Cuenta de entidad",
        grupo="6",
        entidad_id=entidad.id,
        activa=True,
    )
    db.add_all([cuenta_base, cuenta_entidad])
    db.commit()

    respuesta = client.get("/api/v1/cuentas/", params={"entidad_id": str(entidad.id)})
    assert respuesta.status_code == 200
    codigos = [c["codigo"] for c in respuesta.json()]
    assert "43000000" in codigos
    assert "60000001" in codigos


def test_crear_asiento_acepta_cuenta_base_compartida(
    client, crear_usuario, db
):
    from datetime import date

    from app.models.cuenta import Cuenta
    from app.models.entidad import Entidad
    from app.models.ejercicio import Ejercicio

    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad = Entidad(cif="A22222222", nombre="Entidad2", activa=True)
    db.add(entidad)
    db.commit()
    db.refresh(entidad)

    ejercicio = Ejercicio(
        entidad_id=entidad.id,
        anio=2024,
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2024, 12, 31),
        cerrado=False,
    )
    db.add(ejercicio)
    db.commit()
    db.refresh(ejercicio)

    cuenta_base = Cuenta(
        codigo="57000000",
        nombre="Caja base",
        grupo="5",
        entidad_id=None,
        activa=True,
    )
    cuenta_base_haber = Cuenta(
        codigo="41000000",
        nombre="Acreedores base",
        grupo="4",
        entidad_id=None,
        activa=True,
    )
    db.add_all([cuenta_base, cuenta_base_haber])
    db.commit()
    db.refresh(cuenta_base)
    db.refresh(cuenta_base_haber)

    payload = {
        "entidad_id": str(entidad.id),
        "ejercicio_id": str(ejercicio.id),
        "fecha": "2024-01-01",
        "concepto": "Asiento con cuenta base",
        "apuntes": [
            {"cuenta_id": str(cuenta_base.id), "tipo": "debe", "importe": "10.00"},
            {"cuenta_id": str(cuenta_base_haber.id), "tipo": "haber", "importe": "10.00"},
        ],
    }
    respuesta = client.post("/api/v1/asientos/", json=payload)
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["entidad_id"] == str(entidad.id)
    assert datos["ejercicio_id"] == str(ejercicio.id)
    assert len(datos["apuntes"]) == 2


def test_listar_cuentas_de_entidad_sin_cuentas_propias_devuelve_las_del_cuadro_base(
    client, crear_usuario, db
):
    from app.models.cuenta import Cuenta
    from app.models.entidad import Entidad

    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad = Entidad(cif="A11111111", nombre="Entidad1", activa=True)
    otra_entidad = Entidad(cif="B22222222", nombre="Entidad2", activa=True)
    db.add_all([entidad, otra_entidad])
    db.commit()
    db.refresh(entidad)
    db.refresh(otra_entidad)

    db.add_all(
        [
            Cuenta(codigo="430", nombre="Clientes", grupo="4", entidad_id=None, activa=True),
            Cuenta(codigo="100", nombre="Capital social", grupo="1", entidad_id=None, activa=True),
            Cuenta(codigo="200", nombre="Inactiva", grupo="2", entidad_id=None, activa=False),
            Cuenta(codigo="300", nombre="Ajena", grupo="3", entidad_id=otra_entidad.id, activa=True),
        ]
    )
    db.commit()

    respuesta = client.get("/api/v1/cuentas/", params={"entidad_id": str(entidad.id)})

    assert respuesta.status_code == 200
    assert [cuenta["codigo"] for cuenta in respuesta.json()] == ["100", "430"]
