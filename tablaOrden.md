# Orden recomendado de las historias pendientes

| Orden | # | Historia | Razón |
| :-- | :-- | :--- | :--- |
| 1 | 11 | Dar de alta una nueva cuenta hasta 8 dígitos en el cuadro de cuentas base compartido. | Requiere #10 (hecha). Permite ampliar el cuadro con las cuentas necesarias. |
| 2 | 12 | Utilizar las cuentas dadas de alta al registrar movimientos. | Requiere #11. Hace que las cuentas estén disponibles para el registro contable. |
| 3 | 5 | Consultar las transacciones registradas y los saldos. | Requiere #2 (hecha). Es independiente de la importación, por lo que es ideal hacerlo justo después para poder validar lo registrado. |
| 4 | 3 | Importar movimientos bancarios para generar borradores. | Requiere #2 (hecha). Empieza la cadena de importación. |
| 5 | 4 | Revisar, editar o rechazar los borradores de apuntes. | Requiere #3. Completa el flujo de importación. |
| 6 | 8 | Dar de alta a un usuario con nombre, email, contraseña inicial y rol. | Requiere #7 (hecha). Necesario para habilitar el módulo de permisos. |
| 7 | 9 | Avisar cuando el email ya esté en uso o la contraseña sea demasiado corta. | Requiere #8. Mejora la experiencia del alta de usuarios. |
| 8 | 6 | Permisos por rol y separación de responsabilidades en el registro y revisión de apuntes. | Requiere #4 y #8. Al ser el más complejo y necesitar ambas cadenas, lo dejaría para el final, tal y como se indica en AGENTS.md. |
