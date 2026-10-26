## Contexto
Sistema contable para una ONG para registrar transacciones de ingresos y gastos con partida doble conforme a la normativa española y al PGC, con la posibilidad de importar movimientos bancarios generando borradores de apuntes pendientes de revisión. Gestiona entidades con CIF distinto, con libros contables separados y ejercicios contables propios.

## Stack
FastAPI + Node.js (React + Vite) + PostgreSQL. UI con el estándar Google Material Design en todas las pantallas, existentes y futuras.

Librería de UI: MUI (`@mui/material` + Emotion), a instalar al empezar la historia #1. No usar Tailwind ni CSS propio en paralelo: el tema de MUI es la única fuente de verdad del diseño.

## Decisiones costosas
Modelo de permisos o roles

## Documentación
La documentación siempre debe estar en español.

## Backlog
1. Como administrador/a, quiero dar de alta una entidad con su CIF, nombre y ejercicio contable, para poder llevar libros contables separados por cada entidad.
2. Como tesorero/a, quiero registrar una transacción equilibrada de ingresos o gastos con partida doble en la entidad y ejercicio seleccionados, para llevar al día los libros contables de esa entidad. Requiere: #1
3. Como tesorero/a, quiero importar movimientos bancarios desde un archivo para la entidad seleccionada, para generar borradores de apuntes pendientes de revisión. Requiere: #2
4. Como tesorero/a, quiero revisar, editar o rechazar los borradores de apuntes generados por la importación bancaria, para que solo se registren en la contabilidad de esa entidad los apuntes correctos. Requiere: #3
5. Como tesorero/a, quiero consultar las transacciones registradas y los saldos de las cuentas de la entidad y ejercicio seleccionados, para conocer en todo momento la situación financiera de esa entidad. Requiere: #2
6. Como administrador/a, quiero controlar el acceso al registro y a la revisión de apuntes mediante roles, para garantizar la separación de responsabilidades dentro de la ONG. Requiere: #1

