from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def test_un_token_caducado_no_da_acceso(client, crear_usuario):
    usuario = crear_usuario(email="admin@rendo.com")
    caducado = jwt.encode(
        {"sub": usuario.email, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    respuesta = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {caducado}"})

    assert respuesta.status_code == 401
