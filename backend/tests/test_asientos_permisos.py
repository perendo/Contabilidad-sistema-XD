import uuid
from datetime import date

from app.models.ejercicio import Ejercicio
from app.models.entidad import Entidad
from app.models.usuario import RolEnum


def test_solo_lectura_no_puede_crear_asiento_devuelve_403(client, crear_usuario, db):
    crear_usuario(email="lectura@rendo.com", rol=RolEnum.SOLO_LECTURA)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "lectura@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(uuid.uuid4()),
            "ejercicio_id": str(uuid.uuid4()),
            "fecha": "2026-01-01",
            "concepto": "Test",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )

    assert respuesta.status_code == 403


def test_tesorero_puede_crear_asiento(client, crear_usuario, db):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(uuid.uuid4()),
            "ejercicio_id": str(uuid.uuid4()),
            "fecha": "2026-01-01",
            "concepto": "Test",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )

    assert respuesta.status_code == 201


def test_administrador_puede_crear_asiento(client, crear_usuario, db):
    crear_usuario(email="admin2@rendo.com", rol=RolEnum.ADMINISTRADOR)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin2@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(uuid.uuid4()),
            "ejercicio_id": str(uuid.uuid4()),
            "fecha": "2026-01-01",
            "concepto": "Test",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )

    assert respuesta.status_code == 201


def test_crear_asiento_asigna_registrado_por_usuario_autenticado(client, crear_usuario, db):
    usuario = crear_usuario(email="tesorero2@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero2@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(uuid.uuid4()),
            "ejercicio_id": str(uuid.uuid4()),
            "fecha": "2026-01-01",
            "concepto": "Test",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["registrado_por_id"] == str(usuario.id)


def test_crear_asiento_numeracion_secuencial_por_entidad_ejercicio(client, crear_usuario, db):
    crear_usuario(email="tesorero3@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero3@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad = Entidad(cif="A11111111", nombre="Entidad1", activa=True)
    db.add(entidad)
    db.flush()
    ejercicio1 = Ejercicio(entidad_id=entidad.id, anio=2026, fecha_inicio=date(2026, 1, 1), fecha_fin=date(2026, 12, 31))
    ejercicio2 = Ejercicio(entidad_id=entidad.id, anio=2027, fecha_inicio=date(2027, 1, 1), fecha_fin=date(2027, 12, 31))
    db.add_all([ejercicio1, ejercicio2])
    db.commit()

    r1 = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(entidad.id),
            "ejercicio_id": str(ejercicio1.id),
            "fecha": "2026-01-01",
            "concepto": "A1",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )
    r2 = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(entidad.id),
            "ejercicio_id": str(ejercicio1.id),
            "fecha": "2026-01-02",
            "concepto": "A2",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "5.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "5.00"},
            ],
        },
    )
    r3 = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(entidad.id),
            "ejercicio_id": str(ejercicio2.id),
            "fecha": "2027-01-01",
            "concepto": "B1",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 201
    assert r1.json()["numero_asiento"] == 1
    assert r2.json()["numero_asiento"] == 2
    assert r3.json()["numero_asiento"] == 1


def test_crear_asiento_desbalanceado_devuelve_error(client, crear_usuario, db):
    crear_usuario(email="tesorero4@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero4@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(uuid.uuid4()),
            "ejercicio_id": str(uuid.uuid4()),
            "fecha": "2026-01-01",
            "concepto": "Test",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "5.00"},
            ],
        },
    )

    assert respuesta.status_code in (400, 422)


def test_crear_asiento_menos_dos_apuntes_devuelve_error(client, crear_usuario, db):
    crear_usuario(email="tesorero5@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero5@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(uuid.uuid4()),
            "ejercicio_id": str(uuid.uuid4()),
            "fecha": "2026-01-01",
            "concepto": "Test",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "10.00"},
            ],
        },
    )

    assert respuesta.status_code in (400, 422)


def test_crear_asiento_importe_cero_o_negativo_devuelve_error(client, crear_usuario, db):
    crear_usuario(email="tesorero6@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero6@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    respuesta = client.post(
        "/api/v1/asientos",
        json={
            "entidad_id": str(uuid.uuid4()),
            "ejercicio_id": str(uuid.uuid4()),
            "fecha": "2026-01-01",
            "concepto": "Test",
            "apuntes": [
                {"cuenta_id": str(uuid.uuid4()), "tipo": "debe", "importe": "0.00"},
                {"cuenta_id": str(uuid.uuid4()), "tipo": "haber", "importe": "0.00"},
            ],
        },
    )

    assert respuesta.status_code in (400, 422)
