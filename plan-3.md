## Story
Como tesorero/a, quiero importar movimientos bancarios desde un archivo Excel para la entidad y ejercicio seleccionados, eligiendo la cuenta bancaria de destino, para generar borradores de asientos pendientes de revisión.

## Criterios de aceptación
- [ ] Dado un archivo Excel válido con movimientos, una entidad, un ejercicio y una cuenta bancaria seleccionados, cuando importo, entonces se crea un borrador de asiento por movimiento con su fecha, concepto e importe, visible como pendiente de revisión, y veo cuántos borradores se han generado.
- [ ] Dado un movimiento de importe positivo o negativo, cuando se genera su borrador, entonces queda equilibrado en partida doble (cuenta bancaria frente a la cuenta puente 555) con el debe y el haber iguales.
- [ ] Dado un archivo cuyo formato no es válido, que está vacío o que contiene algún movimiento con fecha fuera del ejercicio seleccionado, cuando intento importarlo, entonces no se crea ningún borrador y veo el motivo.
- [ ] Dado un movimiento cuya fecha, importe y concepto coinciden con un borrador o asiento ya existente, cuando importo el archivo, entonces ese movimiento se omite, no se duplica, y veo cuántos se han omitido.

## Plan
- Añadir el estado de borrador a los asientos y un endpoint de importación que reciba el archivo Excel y la cuenta bancaria, validando entidad y ejercicio.
- Parsear los movimientos del Excel (fecha, concepto, importe) y rechazar toda la importación si alguna fecha queda fuera del ejercicio.
- Detectar duplicados por fecha, importe y concepto frente a borradores y asientos existentes, omitiéndolos e informando.
- Generar un borrador equilibrado por movimiento: cuenta bancaria según el signo del importe y la cuenta puente 555 como contrapartida.
- Añadir en el Diario un formulario de importación con selector de archivo y de cuenta bancaria, con resumen de creados, omitidos y errores, y mostrar los borradores pendientes en el listado.

## Fuera de alcance
- Importación en formato norma 43 (queda para otra historia).
- Revisión, edición o rechazo de los borradores (eso es la #4).
- Adjuntar documentos a los borradores.
- Permisos avanzados más allá de exigir tesorería o administración para importar.

## Sugerencias (tu criterio)
- Ninguna por ahora.
