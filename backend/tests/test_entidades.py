def test_crea_entidad_con_su_ejercicio_del_anio_indicado(client):
    respuesta = client.post(
        "/api/v1/entidades",
        json={"cif": "G12345678", "nombre": "Fundación Ejemplo", "anio": 2026},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["cif"] == "G12345678"
    assert datos["nombre"] == "Fundación Ejemplo"
    assert [(e["anio"], e["fecha_inicio"], e["fecha_fin"]) for e in datos["ejercicios"]] == [
        (2026, "2026-01-01", "2026-12-31"),
    ]


def test_rechaza_un_cif_ya_registrado_sin_crear_nada(client):
    datos = {"cif": "G12345678", "nombre": "Fundación Ejemplo", "anio": 2026}
    assert client.post("/api/v1/entidades", json=datos).status_code == 201

    segunda = client.post("/api/v1/entidades", json={**datos, "nombre": "Otra ong", "anio": 2027})

    assert segunda.status_code == 409
    entidades = client.get("/api/v1/entidades").json()
    assert [(e["cif"], len(e["ejercicios"])) for e in entidades] == [("G12345678", 1)]
