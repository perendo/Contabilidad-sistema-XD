def test_el_login_devuelve_token_y_me_identifica_usuario_y_rol(client, crear_usuario):
    crear_usuario(email="admin@rendo.com")

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@rendo.com", "password": "Admin67@"},
    )

    assert login.status_code == 200
    token = login.json()["access_token"]

    yo = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert yo.status_code == 200
    assert yo.json()["email"] == "admin@rendo.com"
    assert yo.json()["rol"]["nombre"] == "administrador"


def test_credenciales_incorrectas_devuelven_401_sin_token(client, crear_usuario):
    crear_usuario(email="admin@rendo.com")

    con_password_mala = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@rendo.com", "password": "OtraClave1@"},
    )
    con_email_inexistente = client.post(
        "/api/v1/auth/login",
        json={"email": "fantasma@rendo.com", "password": "Admin67@"},
    )

    for respuesta in (con_password_mala, con_email_inexistente):
        assert respuesta.status_code == 401
        assert "access_token" not in respuesta.json()
        assert respuesta.json()["detail"] == "Credenciales incorrectas"
