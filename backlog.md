# Backlog

Pendientes del Sistema Contable ONG. **Este fichero es la fuente de verdad de lo que queda por hacer**; lo terminado se anota en el histórico de `AGENTS.md`.

Los identificadores se mantienen estables respecto al backlog original para no romper las dependencias ya escritas. La #1 está completada.

| # | Historia pendiente | Requiere |
|---|---|---|
| 2 | Como tesorero/a, quiero registrar una transacción equilibrada de ingresos o gastos con partida doble en la entidad y ejercicio seleccionados, para llevar al día los libros contables de esa entidad. | #1 (hecha) |
| 3 | Como tesorero/a, quiero importar movimientos bancarios desde un archivo para la entidad seleccionada, para generar borradores de apuntes pendientes de revisión. | #2 |
| 4 | Como tesorero/a, quiero revisar, editar o rechazar los borradores de apuntes generados por la importación bancaria, para que solo se registren en la contabilidad de esa entidad los apuntes correctos. | #3 |
| 5 | Como tesorero/a, quiero consultar las transacciones registradas y los saldos de las cuentas de la entidad y ejercicio seleccionados, para conocer en todo momento la situación financiera de esa entidad. | #2 |
| 6 | Como administrador/a, quiero que cada rol determine qué puede hacer en el registro y la revisión de apuntes, para garantizar la separación de responsabilidades dentro de la ONG. | #4, #8 |
| 7 | Como usuario/a de la ONG, quiero iniciar sesión con mi email y contraseña, para entrar al sistema con el rol que tengo asignado. | — |
| 8 | Como administrador/a, quiero dar de alta a un usuario con su nombre, email, contraseña inicial y rol, para que esa persona pueda entrar al sistema con los permisos que le correspondan. | #7 |

La #6 cubre dos cosas y se refinará por separado cuando existan la #4 y la #8, sin fijar todavía identificadores nuevos:

- **Permisos por rol en apuntes:** solo lectura no registra ni revisa, tesorería registra pero no revisa, administración hace ambas cosas; se ve en la pantalla y se rechaza en la API.
- **Separación de responsabilidades:** quien registró un apunte no puede revisarlo.
