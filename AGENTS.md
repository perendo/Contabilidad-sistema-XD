## Contexto
Sistema contable para una ONG para registrar transacciones de ingresos y gastos con partida doble conforme a la normativa española y al PGC, con la posibilidad de importar movimientos bancarios generando borradores de apuntes pendientes de revisión. Gestiona entidades con CIF distinto, con libros contables separados y ejercicios contables propios.

## Stack
FastAPI + Node.js (React + Vite) + PostgreSQL. UI con el estándar Google Material Design en todas las pantallas, existentes y futuras.

Librería de UI: MUI (`@mui/material` + Emotion), instalada y montada en la historia #1. No usar Tailwind ni CSS propio en paralelo: el tema de MUI es la única fuente de verdad del diseño.

## Decisiones costosas
Modelo de permisos o roles

## Documentación
La documentación siempre debe estar en español.

## Backlog
Los pendientes viven en `backlog.md`, que es la fuente de verdad. Aquí solo se guarda el histórico de lo completado.

## Histórico
- [x] #1 — Dar de alta una entidad con su CIF, nombre y ejercicio contable. Completada el 2026-10-26; falta tu verificación manual del formulario en el navegador.

