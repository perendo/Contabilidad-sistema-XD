# Sistema Contable ONG - PGC España

Sistema contable con partida doble para ONG conforme a la normativa española y al PGC.

## Stack
- Backend: FastAPI + SQLAlchemy + Alembic
- Frontend: Node.js + Vite + React + TypeScript
- Base de datos: PostgreSQL
- Autenticación/roles: Modelo de permisos o roles

## Documentación
Toda la documentación debe estar en español.

## Puesta en marcha (local)

### Clonar el repositorio
Las skills de `.opencode` viven en el submódulo `hola-ai`, así que hay que traerlas:
```bash
git clone --recurse-submodules https://github.com/perendo/Contabilidad-sistema-XD.git
# si ya lo clonaste sin submódulos:
git submodule update --init --recursive
```

### Arranque rápido
Con el entorno virtual creado y las dependencias instaladas:
```bash
py dev.py            # o: python dev.py
```
Levanta el backend y el frontend a la vez (salida prefijada `[api]` / `[web]`), abre el navegador en `/entidades` y para los dos con `Ctrl+C`. Acepta `--no-browser` para no abrir el navegador.

El primer arranque crea el administrador inicial con lo que digan `ADMIN_INICIAL_EMAIL` y `ADMIN_INICIAL_PASSWORD` en `backend/.env` (`admin@ong.org` / `Admin67@` por defecto). Cámbialas antes de usar el sistema de verdad.

### 1) Levantar PostgreSQL
```bash
docker compose up -d
```

### 2) Backend
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
# source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Ejecutar migraciones
alembic upgrade head
# Arrancar servidor
uvicorn app.main:app --reload
```

API: http://localhost:8000
Documentación Swagger: http://localhost:8000/docs

### 3) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Backlog
Ver `AGENTS.md`
