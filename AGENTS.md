# AGENTS.md

## Contexto
Sistema contable para una ONG: ingresos y gastos con partida doble según el PGC español, entidades con CIF y ejercicios propios, importación bancaria con borradores y justificantes adjuntos al asiento.

## Stack y arranque
- Backend: FastAPI + SQLAlchemy + Alembic en `backend/`. Frontend: React + Vite + TypeScript + MUI en `frontend/`. Base de datos: PostgreSQL; en desarrollo, SQLite por defecto.
- Desarrollo: `py dev.py` (o `start.bat`) desde la raíz. Levanta uvicorn en el puerto 8000 y Vite en el 5173 con salida `[api]`/`[web]`; `--no-browser` evita abrir `/entidades`. Exige `backend/.venv`, `frontend/node_modules` y los puertos libres.
- `dev.py` no ejecuta migraciones. En un clon nuevo: `cd backend` y después `alembic upgrade head`.
- `backend/.env.example` trae `USE_SQLITE=true`: el desarrollo y los tests usan SQLite (`backend/contabilidad.db`), no PostgreSQL. `docker compose up -d` solo hace falta si pones `USE_SQLITE=false`.
- Ejecuta los comandos de backend desde `backend/`: `settings` carga `.env` relativo al directorio actual. Si arrancas `uvicorn`, `alembic` o `pytest` desde la raíz, usarás otra configuración y otra base SQLite.
- El primer arranque siembra los tres roles, el administrador (`ADMIN_INICIAL_EMAIL`/`ADMIN_INICIAL_PASSWORD`; por defecto `admin@ong.org`/`Admin67@`) y las 421 cuentas del PGC desde `backend/app/db/pgc.py`. Con PostgreSQL se niega a arrancar con la contraseña de fábrica.

## Verificación
- Backend, desde `backend/`: `.venv\Scripts\python.exe -m pytest -q` (Windows) o `python -m pytest -q` con el entorno activado.
- Un solo test: `.venv\Scripts\python.exe -m pytest -q tests/test_cuentas_base.py::test_...`.
- Los tests usan SQLite en memoria y sustituyen `get_db`; no necesitan PostgreSQL ni Docker. Fixtures en `backend/tests/conftest.py`: `client`, `cliente_admin`, `cliente_tesorero`, `cliente_solo_lectura`, `crear_usuario`; los usuarios de test usan la contraseña `Admin67@`.
- La suite completa es intermitente: el motor de test comparte una única conexión SQLite (`StaticPool`) entre la sesión del test y la petición. Si aparece un fallo raro (por ejemplo, `AttributeError: 'float' object has no attribute 'replace'` al refrescar un UUID), repite ese test solo antes de buscar una regresión.
- El frontend no tiene tests ni lint: `cd frontend` y `npm run build` es la verificación (tsc estricto con `noUnusedLocals`/`noUnusedParameters`).
- Los tests crean las tablas con `Base.metadata.create_all` y no ejecutan Alembic. Un cambio en `app/models/` necesita una revisión manual en `backend/alembic/versions/` (usa `batch_alter_table`; `env.py` ya configura `render_as_batch=True`) o el arranque real fallará.
- Al añadir un modelo, impórtalo en `backend/app/models/__init__.py`; Alembic y los tests solo registran lo que se importa ahí.

## Estructura y convenciones
- API en `/api/v1`. Todo salvo `/auth` exige `Authorization: Bearer`; el frontend guarda el token en `sessionStorage` (`frontend/src/api/cliente.ts`) y CORS solo admite `http://localhost:5173`.
- Routers en `backend/app/api/v1/endpoints/`; permisos en `backend/app/api/deps.py` (`solo_administrador`, `solo_tesorero_o_admin`); modelos, esquemas y configuración en `app/models/`, `app/schemas/` y `app/core/`.
- Frontend: `src/pages/` pantallas, `src/components/MarcoApp.tsx` layout, `src/sesion.tsx` contexto de sesión/entidad/ejercicio, `src/theme.ts` tema MUI.
- UI: MUI + Emotion es la única fuente de diseño. No añadas Tailwind ni CSS propio en paralelo (solo existe el reset de `index.css`). Está pensada para escritorio, no para móvil.
- Escribe en español nombres de código, tests, mensajes de error, documentación y commits, como el resto del repo.
- Documentos adjuntos: se guardan en `backend/data/<CIF>/<año>/` (configurable con `DIRECTORIO_DATOS`); `backend/data/` y `backend/documentos/` (legado) no se versionan.

## Decisiones costosas
- Permisos: un rol fijo por usuario (`administrador`, `tesorero`, `solo_lectura`), global a la ONG, no por entidad. La API lo comprueba y la UI lo refleja; la matriz completa se fija en la #6.
- Cuentas: cuadro base del PGC compartido en `cuentas` con `entidad_id` NULL, ampliable con cuentas propias hasta 8 dígitos. `GET /cuentas?entidad_id=...` devuelve las propias más las base.
- Justificantes: varios documentos por asiento (no por apunte), PDF/JPG/PNG de hasta 10 MB. Solo tesorería y administración adjuntan o eliminan; solo lectura consulta y descarga (la eliminación es la #16).
- La #6 requiere antes la #3 (importación bancaria) y la #4 (revisión de borradores). Se entregará en dos partes: permisos por rol en apuntes y, después, separación de responsabilidades.

## Flujo de trabajo
- `backlog.md` es la fuente de verdad de lo pendiente; este archivo solo conserva el histórico de lo completado.
- Los planes de historia se escriben como `plan-N.md` en la raíz y, al cerrar la historia, se mueven a `historico plan/`.
- Los comandos locales `/story`, `/pair` y `/backlog` (`.opencode/commands/`) cargan las skills del submódulo `hola-ai`. Si faltan: `git submodule update --init --recursive`.
- `/pair` trabaja con TDD en pasos pequeños y nunca hace commits: el usuario revisa y commitea.

## Histórico
- [x] #1 — Dar de alta una entidad con su CIF, nombre y ejercicio contable. Completada el 2026-10-26; falta tu verificación manual del formulario en el navegador.
- [x] #2 — Registrar una transacción equilibrada de ingresos o gastos con partida doble en la entidad y ejercicio seleccionados. Completada el 2026-10-27. Los tests cubren el alta equilibrada, la numeración secuencial por entidad/ejercicio, el rechazo de asientos inválidos y el 403 para solo lectura (`backend/tests/test_asientos_permisos.py`).
- [x] #3 — Importar movimientos bancarios desde un archivo Excel para la entidad y ejercicio seleccionados, generando borradores de asientos pendientes de revisión (cuenta bancaria frente a la puente 555). Completada el 2026-10-30. Incluye validación de fechas, duplicados, tamaño y formato, y migraciones `6e8f0c3d5b21`/`7a0b1c2d3e4f`. Tests en `backend/tests/test_importacion_bancaria.py`.
- [x] #4 — Revisar, editar, aprobar o rechazar los borradores generados por la importación bancaria, para que solo se registren los apuntes correctos. Completada el 2026-10-30. Endpoints `PATCH /asientos/{id}`, `POST /asientos/{id}/aprobar` y `DELETE /asientos/{id}`, con edición de apuntes y gestión desde el Diario. Tests en `backend/tests/test_borradores.py`.
- [x] #8 — Dar de alta a un usuario con nombre, email, contraseña inicial y rol. Completada el 2026-10-27 (commit `cd32510`) y cerrada en el backlog el 2026-10-28; falta tu verificación manual en el navegador. El alta y el listado quedan reservados a administración (403 en la API y sección oculta en el menú), la contraseña se guarda cifrada y el usuario creado puede iniciar sesión. Tests en `backend/tests/test_usuarios.py`.
- [x] #7 — Iniciar sesión con email y contraseña y mantener el rol asignado. Completada y verificada a mano en el navegador el 2026-10-26. Al arrancar se siembran los tres roles y el administrador inicial, con las credenciales de la configuración.
- [x] #10 — Consultar el cuadro de cuentas base compartido del PGC hasta 3 dígitos. Completada y verificada a mano en el navegador el 2026-10-27. Se siembran 421 cuentas del PGC (RD 1514/2007) desde `backend/app/db/pgc.py` y se exponen en solo lectura a tesorería y administración.
- [x] #11 — Dar de alta una nueva cuenta hasta 8 dígitos en el cuadro de cuentas base compartido. Completada el 2026-10-28. Se permite crear cuentas base (`entidad_id` NULL) con código numérico hasta 8 dígitos, restringido a tesorero/a o administrador/a, con unicidad en el cuadro base y mensaje específico en caso de duplicado; se valida también para cuentas por entidad manteniéndose la unicidad por entidad. Tests en `backend/tests/test_cuentas_base.py`.
- [x] #12 — Utilizar las cuentas del cuadro de cuentas base compartido al registrar movimientos. Completada el 2026-10-28. `GET /cuentas` con `entidad_id` devuelve las cuentas de esa entidad junto con las cuentas base (`entidad_id` NULL), y el alta de asientos acepta cuentas base; el selector de asientos ya consume ese listado. Tests en `backend/tests/test_cuentas_base.py`.
- [x] #13 — Que al registrar un asiento se carguen sin errores las cuentas de la entidad y el listado de asientos. Completada el 2026-10-28. Los listados de cuentas y de asientos aceptan los ids como UUID (antes devolvían 500 con los ids en texto), el selector une las cuentas propias con el cuadro base y, al guardar, se muestra «Asiento guardado correctamente» con los avisos de carga y de guardado separados. Tests en `backend/tests/test_asientos_listado.py` y `backend/tests/test_cuentas_base.py`. Tras el último ajuste de contexto conviene re-comprobar en el navegador el cambio de entidad/ejercicio con el formulario a medio rellenar.
