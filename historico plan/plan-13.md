## Historia
Como tesorero/a, quiero que al abrir el registro de asientos se carguen sin errores las cuentas de la entidad y los asientos ya registrados, para poder elegir la cuenta contable y comprobar lo anotado.

## Criterios de aceptación
- [ ] Dado que he iniciado sesión como tesorero/a y he seleccionado una entidad y un ejercicio, cuando abro el registro de asientos, entonces el selector muestra las cuentas propias de la entidad junto con las del cuadro base y el listado de asientos ya registrados se carga sin ningún mensaje de error.
- [ ] Dado que la entidad seleccionada no tiene cuentas propias, cuando abro el selector de cuentas, entonces puedo elegir igualmente cualquier cuenta del cuadro base.
- [ ] Dado que guardo un asiento equilibrado con una cuenta del cuadro base o de la entidad, cuando termina el guardado, entonces el asiento aparece en el listado, se muestra el aviso «Asiento guardado correctamente», no aparece ningún mensaje de error y se ha creado una sola vez.

## Plan
- Aceptar el identificador de entidad y de ejercicio que llega del navegador como identificador validado, no como texto libre.
- Resolver el listado de cuentas en la consulta: cuentas activas de la entidad seleccionada más las del cuadro base, ordenadas por código.
- Resolver el listado de asientos por entidad y ejercicio con esos mismos identificadores validados.
- Separar en la pantalla el aviso de «no se pudo cargar» del de «no se pudo guardar», para no dar por fallido un asiento que ya se registró.
- Cubrir con pruebas de API las llamadas tal y como las hace el navegador (ids en texto), con una entidad con cuentas propias y con otra que solo tenga cuentas base.

## Fuera de alcance
- Permisos por rol y separación de responsabilidades (#6).
- Alta o edición de cuentas, importación bancaria y revisión de borradores (#3, #4, #11).
- Paginación o búsqueda en servidor del cuadro de cuentas.
- Cambiar la numeración o las validaciones de partida doble de los asientos.

## Sugerencias (a tu criterio)
- El mismo patrón de identificador en texto contra columna UUID se repite al consultar una cuenta concreta y un asiento concreto; si se toca, conviene corregirlo en los tres sitios a la vez.
- Con más de 421 cuentas en el selector, un filtro por código o nombre al escribir ahorraría scroll; no hace falta para cumplir los criterios.
