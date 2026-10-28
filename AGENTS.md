## Contexto
Sistema contable para una ONG para registrar transacciones de ingresos y gastos con partida doble conforme a la normativa española y al PGC, con la posibilidad de importar movimientos bancarios generando borradores de apuntes pendientes de revisión. Gestiona entidades con CIF distinto, con libros contables separados y ejercicios contables propios.

## Stack
FastAPI + Node.js (React + Vite) + PostgreSQL. UI con el estándar Google Material Design en todas las pantallas, existentes y futuras.

Librería de UI: MUI (`@mui/material` + Emotion), instalada y montada en la historia #1. No usar Tailwind ni CSS propio en paralelo: el tema de MUI es la única fuente de verdad del diseño.

La aplicación se usa en equipos de escritorio: no se diseña ni se verifica para móvil.

## Decisiones costosas
Modelo de permisos o roles: un rol por usuario, elegido entre tres fijos (administrador/a, tesorero/a y solo lectura). Los usuarios son globales a la ONG, no por entidad. El rol se comprueba en la API y se refleja en la interfaz; la matriz de qué puede hacer cada rol en cada módulo se fija al construir la #6.
Cuadro de cuentas base compartido entre todas las entidades (PGC español hasta 3 dígitos ya definido), ampliable con cuentas propias hasta 8 dígitos. Las cuentas compartidas se guardan en `cuentas` con `entidad_id` NULL; las de una entidad llevan su `entidad_id`. Al listar cuentas con `entidad_id`, `GET /cuentas` incluye también las cuentas base con `entidad_id` NULL, ya que son utilizables en cualquier entidad.

## Documentación
La documentación siempre debe estar en español.

## Backlog
Los pendientes viven en `backlog.md`, que es la fuente de verdad. Aquí solo se guarda el histórico de lo completado.

Para completar la #6 (permisos por rol y separación de responsabilidades) hace falta, en este orden, la #3 (importación bancaria) y la #4 (revisión de borradores); la #2 (registro equilibrado) y la #8 (alta de usuario con rol) ya están hechas. La #6 se entregará en dos partes: permisos por rol en apuntes y, después, separación de responsabilidades.

## Histórico
- [x] #1 — Dar de alta una entidad con su CIF, nombre y ejercicio contable. Completada el 2026-10-26; falta tu verificación manual del formulario en el navegador.
- [x] #2 — Registrar una transacción equilibrada de ingresos o gastos con partida doble en la entidad y ejercicio seleccionados. Completada el 2026-10-27. Los tests cubren el alta equilibrada, la numeración secuencial por entidad/ejercicio, el rechazo de asientos inválidos y el 403 para solo lectura (`backend/tests/test_asientos_permisos.py`).
- [x] #8 — Dar de alta a un usuario con nombre, email, contraseña inicial y rol. Completada el 2026-10-27 (commit `cd32510`) y cerrada en el backlog el 2026-10-28; falta tu verificación manual en el navegador. El alta y el listado quedan reservados a administración (403 en la API y sección oculta en el menú), la contraseña se guarda cifrada y el usuario creado puede iniciar sesión. Tests en `backend/tests/test_usuarios.py`.
- [x] #7 — Iniciar sesión con email y contraseña y mantener el rol asignado. Completada y verificada a mano en el navegador el 2026-10-26. Al arrancar se siembran los tres roles y el administrador inicial, con las credenciales de la configuración.
- [x] #10 — Consultar el cuadro de cuentas base compartido del PGC hasta 3 dígitos. Completada y verificada a mano en el navegador el 2026-10-27. Se siembran 421 cuentas del PGC (RD 1514/2007) desde `backend/app/db/pgc.py` y se exponen en solo lectura a tesorería y administración.
- [x] #11 — Dar de alta una nueva cuenta hasta 8 dígitos en el cuadro de cuentas base compartido. Completada el 2026-10-28. Se permite crear cuentas base (`entidad_id` NULL) con código numérico hasta 8 dígitos, restringido a tesorero/a o administrador/a, con unicidad en el cuadro base y mensaje específico en caso de duplicado; se valida también para cuentas por entidad manteniéndose la unicidad por entidad. Tests en `backend/tests/test_cuentas_base.py`.
- [x] #12 — Utilizar las cuentas del cuadro de cuentas base compartido al registrar movimientos. Completada el 2026-10-28. `GET /cuentas` con `entidad_id` devuelve las cuentas de esa entidad junto con las cuentas base (`entidad_id` NULL), y el alta de asientos acepta cuentas base; el selector de asientos ya consume ese listado. Tests en `backend/tests/test_cuentas_base.py`.
- [x] #13 — Que al registrar un asiento se carguen sin errores las cuentas de la entidad y el listado de asientos. Completada el 2026-10-28. Los listados de cuentas y de asientos aceptan los ids como UUID (antes devolvían 500 con los ids en texto), el selector une las cuentas propias con el cuadro base y, al guardar, se muestra «Asiento guardado correctamente» con los avisos de carga y de guardado separados. Tests en `backend/tests/test_asientos_listado.py` y `backend/tests/test_cuentas_base.py`. Tras el último ajuste de contexto conviene re-comprobar en el navegador el cambio de entidad/ejercicio con el formulario a medio rellenar.

