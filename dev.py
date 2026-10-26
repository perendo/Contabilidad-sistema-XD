#!/usr/bin/env python3
"""Arranca el entorno de desarrollo del Sistema Contable ONG.

Levanta el backend (uvicorn con recarga automática) usando el Python del
entorno virtual de `backend/.venv` y el frontend (Vite) de `frontend/`.
Los dos servidores se paran a la vez con Ctrl+C.
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import NoReturn

RAIZ = Path(__file__).resolve().parent
DIR_BACKEND = RAIZ / "backend"
DIR_FRONTEND = RAIZ / "frontend"
PUERTO_API = 8000
PUERTO_WEB = 5173
URL_WEB = f"http://localhost:{PUERTO_WEB}/entidades"
SEGUNDOS_ESPERA_NAVEGADOR = 30


def salir(mensaje: str) -> NoReturn:
    print(f"ERROR: {mensaje}", file=sys.stderr)
    raise SystemExit(1)


def python_del_venv() -> Path:
    for relativa in ("Scripts/python.exe", "bin/python"):
        ruta = DIR_BACKEND / ".venv" / relativa
        if ruta.exists():
            return ruta
    salir(
        "no encuentro el entorno virtual en backend/.venv.\n"
        "Créalo con:\n"
        "  cd backend\n"
        "  python -m venv .venv\n"
        "  .venv\\Scripts\\pip install -r requirements.txt"
    )


def puerto_ocupado(puerto: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
        conexion.settimeout(0.5)
        return conexion.connect_ex(("127.0.0.1", puerto)) == 0


def reenviar_salida(proceso: subprocess.Popen, prefijo: str) -> None:
    assert proceso.stdout is not None
    for linea in proceso.stdout:
        print(f"{prefijo} {linea.rstrip()}", flush=True)


def arrancar(comando: list[str], directorio: Path, prefijo: str) -> subprocess.Popen:
    proceso = subprocess.Popen(
        comando,
        cwd=directorio,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    threading.Thread(target=reenviar_salida, args=(proceso, prefijo), daemon=True).start()
    return proceso


def detener(procesos: list[subprocess.Popen]) -> None:
    for proceso in procesos:
        if proceso.poll() is not None:
            continue
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proceso.pid)], capture_output=True)
        else:
            proceso.terminate()
    for proceso in procesos:
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()


def abrir_navegador_cuando_responda() -> None:
    limite = time.time() + SEGUNDOS_ESPERA_NAVEGADOR
    while time.time() < limite:
        if puerto_ocupado(PUERTO_WEB):
            webbrowser.open(URL_WEB)
            return
        time.sleep(0.5)


def analizar_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(description="Arranca backend y frontend en modo desarrollo.")
    analizador.add_argument("--no-browser", action="store_true", help="no abrir el navegador al arrancar")
    return analizador.parse_args()


def main() -> int:
    argumentos = analizar_argumentos()
    python = python_del_venv()
    npm = shutil.which("npm")
    if npm is None:
        salir("no encuentro npm en el PATH.")
    if not (DIR_FRONTEND / "node_modules").is_dir():
        salir("faltan las dependencias del frontend. Ejecuta `npm install` en frontend/.")

    for puerto, nombre in ((PUERTO_API, "API"), (PUERTO_WEB, "frontend")):
        if puerto_ocupado(puerto):
            salir(f"el puerto {puerto} ({nombre}) ya está en uso. Para lo que esté escuchando ahí o cambia el puerto en dev.py.")

    print("Arrancando entorno de desarrollo")
    print(f"  API:  http://localhost:{PUERTO_API}/docs")
    print(f"  Web:  {URL_WEB}")
    print("  Ctrl+C para parar ambos servidores\n")

    procesos = [
        arrancar(
            [str(python), "-m", "uvicorn", "app.main:app", "--reload", "--port", str(PUERTO_API)],
            DIR_BACKEND,
            "[api]",
        ),
        arrancar([npm, "run", "dev"], DIR_FRONTEND, "[web]"),
    ]

    if not argumentos.no_browser:
        threading.Thread(target=abrir_navegador_cuando_responda, daemon=True).start()

    try:
        while True:
            for proceso, nombre in zip(procesos, ("api", "web")):
                if proceso.poll() is not None:
                    print(f"\n[{nombre}] ha terminado con código {proceso.returncode}. Parando el resto.")
                    return proceso.returncode or 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nParando servidores...")
        return 0
    finally:
        detener(procesos)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
