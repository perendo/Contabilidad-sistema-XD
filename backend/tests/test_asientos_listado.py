from datetime import date
from decimal import Decimal

from app.models.asiento import Apunte, Asiento, TipoApunte
from app.models.cuenta import Cuenta
from app.models.entidad import Entidad
from app.models.ejercicio import Ejercicio
from app.models.usuario import RolEnum


def _contexto(db, cif="A11111111", nombre="Entidad1", anio=2026):
    entidad = Entidad(cif=cif, nombre=nombre, activa=True)
    db.add(entidad)
    db.flush()
    ejercicio = Ejercicio(
        entidad_id=entidad.id,
        anio=anio,
        fecha_inicio=date(anio, 1, 1),
        fecha_fin=date(anio, 12, 31),
    )
    db.add(ejercicio)
    db.flush()
    return entidad, ejercicio


def _contexto_con_asiento(
    db, usuario, cif="A11111111", nombre="Entidad1", anio=2026, concepto="Compra de material"
):
    entidad, ejercicio = _contexto(db, cif=cif, nombre=nombre, anio=anio)
    debe = Cuenta(codigo="600", nombre="Compras", grupo="6", activa=True)
    haber = Cuenta(codigo="570", nombre="Caja", grupo="5", activa=True)
    db.add_all([debe, haber])
    db.flush()
    asiento = Asiento(
        entidad_id=entidad.id,
        ejercicio_id=ejercicio.id,
        numero_asiento=1,
        fecha=date(anio, 1, 15),
        concepto=concepto,
        registrado_por_id=usuario.id,
    )
    db.add(asiento)
    db.flush()
    db.add_all(
        [
            Apunte(asiento_id=asiento.id, cuenta_id=debe.id, tipo=TipoApunte.DEBE, importe=Decimal("10.00")),
            Apunte(asiento_id=asiento.id, cuenta_id=haber.id, tipo=TipoApunte.HABER, importe=Decimal("10.00")),
        ]
    )
    db.commit()
    return entidad, ejercicio


def test_listar_asientos_por_entidad_y_ejercicio_con_ids_en_texto_devuelve_el_listado(
    client, crear_usuario, db
):
    usuario = crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad, ejercicio = _contexto_con_asiento(db, usuario)
    _contexto_con_asiento(
        db, usuario, cif="B22222222", nombre="Entidad2", anio=2027, concepto="Otra entidad"
    )

    respuesta = client.get(
        "/api/v1/asientos/",
        params={"entidad_id": str(entidad.id), "ejercicio_id": str(ejercicio.id)},
    )

    assert respuesta.status_code == 200
    assert [asiento["concepto"] for asiento in respuesta.json()] == ["Compra de material"]


def test_asiento_creado_con_cuenta_base_aparece_una_sola_vez_en_el_listado(
    client, crear_usuario, db
):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad, ejercicio = _contexto(db)
    debe = Cuenta(codigo="621", nombre="Arrendamientos", grupo="6", entidad_id=None, activa=True)
    haber = Cuenta(codigo="572", nombre="Bancos", grupo="5", entidad_id=None, activa=True)
    db.add_all([debe, haber])
    db.commit()

    alta = client.post(
        "/api/v1/asientos/",
        json={
            "entidad_id": str(entidad.id),
            "ejercicio_id": str(ejercicio.id),
            "fecha": "2026-01-15",
            "concepto": "Alquiler de enero",
            "apuntes": [
                {"cuenta_id": str(debe.id), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(haber.id), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )
    assert alta.status_code == 201

    listado = client.get(
        "/api/v1/asientos/",
        params={"entidad_id": str(entidad.id), "ejercicio_id": str(ejercicio.id)},
    )

    assert listado.status_code == 200
    assert [asiento["id"] for asiento in listado.json()] == [alta.json()["id"]]


def test_asiento_creado_con_cuenta_de_la_entidad_aparece_en_el_listado(
    client, crear_usuario, db
):
    crear_usuario(email="tesorero@rendo.com", rol=RolEnum.TESORERO)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tesorero@rendo.com", "password": "Admin67@"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    entidad, ejercicio = _contexto(db)
    debe = Cuenta(codigo="629", nombre="Otros gastos", grupo="6", entidad_id=entidad.id, activa=True)
    haber = Cuenta(codigo="551", nombre="Cuenta corriente", grupo="5", entidad_id=entidad.id, activa=True)
    db.add_all([debe, haber])
    db.commit()

    alta = client.post(
        "/api/v1/asientos/",
        json={
            "entidad_id": str(entidad.id),
            "ejercicio_id": str(ejercicio.id),
            "fecha": "2026-01-16",
            "concepto": "Gastos propios",
            "apuntes": [
                {"cuenta_id": str(debe.id), "tipo": "debe", "importe": "10.00"},
                {"cuenta_id": str(haber.id), "tipo": "haber", "importe": "10.00"},
            ],
        },
    )
    assert alta.status_code == 201

    listado = client.get(
        "/api/v1/asientos/",
        params={"entidad_id": str(entidad.id), "ejercicio_id": str(ejercicio.id)},
    )

    assert listado.status_code == 200
    assert [asiento["id"] for asiento in listado.json()] == [alta.json()["id"]]
