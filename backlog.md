# Backlog

Pendientes del Sistema Contable ONG. **Este fichero es la fuente de verdad de lo que queda por hacer**; lo terminado se anota en el histórico de `AGENTS.md`.

Los identificadores se mantienen estables respecto al backlog original para no romper las dependencias ya escritas. La #1, la #2, la #7 y la #10 están completadas.

| # | Historia pendiente | Requiere |
|---|---|---|
| 3 | Como tesorero/a, quiero importar movimientos bancarios desde un archivo para la entidad seleccionada, para generar borradores de apuntes pendientes de revisión. | #2 (hecha) |
| 4 | Como tesorero/a, quiero revisar, editar o rechazar los borradores de apuntes generados por la importación bancaria, para que solo se registren en la contabilidad de esa entidad los apuntes correctos. | #3 |
| 5 | Como tesorero/a, quiero consultar las transacciones registradas y los saldos de las cuentas de la entidad y ejercicio seleccionados, para conocer en todo momento la situación financiera de esa entidad. | #2 (hecha) |
| 6 | Como administrador/a, quiero que cada rol determine qué puede hacer en el registro y la revisión de apuntes, para garantizar la separación de responsabilidades dentro de la ONG. | #4, #8 |
| 8 | Como administrador/a, quiero dar de alta a un usuario con su nombre, email, contraseña inicial y rol, para que esa persona pueda entrar al sistema con los permisos que le correspondan. | #7 (hecha) |
| 9 | Como administrador/a, quiero que el alta de usuario me avise cuando el email ya está en uso o la contraseña es demasiado corta, para no crear cuentas repetidas ni débiles. | #8 |
| 11 | Como tesorero/a, quiero dar de alta una nueva cuenta hasta 8 dígitos en el cuadro de cuentas base compartido, para ampliarlo con las cuentas que necesito para mis operaciones. | #10 (hecha) |
| 12 | Como tesorero/a, quiero poder utilizar las cuentas dadas de alta en el cuadro de cuentas base compartido al registrar movimientos, para usarlas inmediatamente en cualquier entidad. | #11 |
| 13 | Como tesorero/a, quiero que las cuentas de una entidad se carguen sin errores al registrar un asiento, para poder elegir la cuenta contable. | |

La #6 cubre dos cosas y se refinará por separado cuando existan la #4 y la #8, sin fijar todavía identificadores nuevos:

- **Permisos por rol en apuntes:** solo lectura no registra ni revisa, tesorería registra pero no revisa, administración hace ambas cosas; se ve en la pantalla y se rechaza en la API.
- **Separación de responsabilidades:** quien registró un apunte no puede revisarlo.

## Notas técnicas

- Pendiente al cerrar la #10: garantizar en base de datos la unicidad e idempotencia del cuadro base con varios procesos de arranque (índice único parcial) y valorar paginación o búsqueda en servidor cuando llegue la #11.
