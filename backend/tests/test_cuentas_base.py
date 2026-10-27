from app.db.seed import sembrar_datos_iniciales
from app.models.cuenta import Cuenta
from app.models.entidad import Entidad


def test_sin_sesion_no_se_puede_consultar_el_cuadro_base(client):
    respuesta = client.get("/api/v1/cuentas/base")

    assert respuesta.status_code == 401


def test_tesorero_consulta_el_cuadro_base_y_recibe_codigos_de_hasta_tres_digitos(cliente_tesorero, db):
    sembrar_datos_iniciales(db)

    respuesta = cliente_tesorero.get("/api/v1/cuentas/base")

    assert respuesta.status_code == 200
    codigos = [cuenta["codigo"] for cuenta in respuesta.json()]
    assert codigos
    assert all(codigo.isdigit() and len(codigo) <= 3 for codigo in codigos)


def test_cada_cuenta_base_incluye_codigo_y_nombre_del_pgc(cliente_tesorero, db):
    sembrar_datos_iniciales(db)

    respuesta = cliente_tesorero.get("/api/v1/cuentas/base")

    assert respuesta.status_code == 200
    cuentas = respuesta.json()
    assert all(cuenta["codigo"] and cuenta["nombre"] for cuenta in cuentas)
    por_codigo = {cuenta["codigo"]: cuenta["nombre"] for cuenta in cuentas}
    assert por_codigo["100"] == "Capital social"
    assert por_codigo["430"] == "Clientes"
    assert por_codigo["293"] == "Deterioro de valor de participaciones a largo plazo en partes vinculadas"
    assert por_codigo["500"] == "Obligaciones y bonos a corto plazo"
    assert por_codigo["501"] == "Obligaciones y bonos convertibles a corto plazo"
    assert por_codigo["502"] == "Acciones o participaciones a corto plazo consideradas como pasivos financieros"
    assert por_codigo["664"] == "Dividendos de acciones o participaciones consideradas como pasivos financieros"


def test_el_catalogo_base_tiene_las_421_cuentas_del_pgc(cliente_tesorero, db):
    sembrar_datos_iniciales(db)

    cuentas = cliente_tesorero.get("/api/v1/cuentas/base").json()

    assert len(cuentas) == 421


def test_solo_lectura_no_puede_consultar_el_cuadro_base(cliente_solo_lectura, db):
    sembrar_datos_iniciales(db)

    respuesta = cliente_solo_lectura.get("/api/v1/cuentas/base")

    assert respuesta.status_code == 403


def test_administrador_puede_consultar_el_cuadro_base(cliente_admin, db):
    sembrar_datos_iniciales(db)

    respuesta = cliente_admin.get("/api/v1/cuentas/base")

    assert respuesta.status_code == 200


def test_el_cuadro_base_se_consulta_sin_entidad_ni_ejercicio(cliente_tesorero, db):
    sembrar_datos_iniciales(db)

    respuesta = cliente_tesorero.get("/api/v1/cuentas/base")

    assert respuesta.status_code == 200
    cuentas = respuesta.json()
    assert cuentas
    assert all(cuenta["entidad_id"] is None for cuenta in cuentas)


def test_las_cuentas_de_una_entidad_no_aparecen_en_el_cuadro_base(cliente_tesorero, db):
    sembrar_datos_iniciales(db)
    entidad = Entidad(cif="G12345678", nombre="Entidad con cuentas propias", activa=True)
    db.add(entidad)
    db.flush()
    db.add(Cuenta(entidad_id=entidad.id, codigo="9999", nombre="Cuenta propia", grupo="9"))
    db.commit()

    base = cliente_tesorero.get("/api/v1/cuentas/base")

    assert base.status_code == 200
    assert "Cuenta propia" not in {cuenta["nombre"] for cuenta in base.json()}
    assert all(cuenta["entidad_id"] is None for cuenta in base.json())


def test_el_cuadro_base_es_solo_lectura(cliente_tesorero, db):
    sembrar_datos_iniciales(db)

    antes = cliente_tesorero.get("/api/v1/cuentas/base").json()

    for metodo in ("post", "put", "delete"):
        respuesta = getattr(cliente_tesorero, metodo)("/api/v1/cuentas/base")
        assert respuesta.status_code == 405

    despues = cliente_tesorero.get("/api/v1/cuentas/base").json()
    assert despues == antes


def test_una_cuenta_de_entidad_puede_reutilizar_un_codigo_del_pgc(cliente_tesorero, db):
    sembrar_datos_iniciales(db)
    entidad = Entidad(cif="G12345678", nombre="Entidad con cuenta 430", activa=True)
    db.add(entidad)
    db.commit()

    respuesta = cliente_tesorero.post(
        "/api/v1/cuentas",
        json={
            "entidad_id": str(entidad.id),
            "codigo": "430",
            "nombre": "Clientes de la entidad",
            "grupo": "4",
        },
    )

    assert respuesta.status_code == 201
