## Contexto
Sistema contable para una ONG para registrar transacciones de ingresos y gastos con partida doble conforme a la normativa española y al PGC, con la posibilidad de importar movimientos bancarios generando borradores de apuntes pendientes de revisión. Gestiona entidades con CIF distinto, con libros contables separados y ejercicios contables propios.

## Stack
FastAPI + Node.js (React + Vite) + PostgreSQL. UI con el estándar Google Material Design en todas las pantallas, existentes y futuras.

Librería de UI: MUI (`@mui/material` + Emotion), instalada y montada en la historia #1. No usar Tailwind ni CSS propio en paralelo: el tema de MUI es la única fuente de verdad del diseño.

La aplicación se usa en equipos de escritorio: no se diseña ni se verifica para móvil.

## Decisiones costosas
Modelo de permisos o roles: un rol por usuario, elegido entre tres fijos (administrador/a, tesorero/a y solo lectura). Los usuarios son globales a la ONG, no por entidad. El rol se comprueba en la API y se refleja en la interfaz; la matriz de qué puede hacer cada rol en cada módulo se fija al construir la #6.

## Documentación
La documentación siempre debe estar en español.

## Backlog
Los pendientes viven en `backlog.md`, que es la fuente de verdad. Aquí solo se guarda el histórico de lo completado.

Para completar la #6 (permisos por rol y separación de responsabilidades) hace falta, en este orden, la #8 (alta de usuario con rol), la #2 (registro equilibrado), la #3 (importación bancaria) y la #4 (revisión de borradores). La #6 se entregará en dos partes: permisos por rol en apuntes y, después, separación de responsabilidades.

## Histórico
- [x] #1 — Dar de alta una entidad con su CIF, nombre y ejercicio contable. Completada el 2026-10-26; falta tu verificación manual del formulario en el navegador.
- [x] #7 — Iniciar sesión con email y contraseña y mantener el rol asignado. Completada y verificada a mano en el navegador el 2026-10-26. Al arrancar se siembran los tres roles y el administrador inicial, con las credenciales de la configuración.

