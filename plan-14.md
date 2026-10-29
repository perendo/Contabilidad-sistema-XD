## Historia
Como tesorero/a, quiero adjuntar uno o varios documentos PDF, JPG o PNG de hasta 10 MB al registrar un asiento y poder consultarlos y descargarlos después desde ese asiento, para que el libro diario conserve la factura o el recibo que justifica cada apunte.

## Criterios de aceptación
- [ ] Dado el formulario de nuevo asiento rellenado, cuando adjunto uno o varios PDF/JPG/PNG de hasta 10 MB cada uno y guardo, entonces el asiento queda registrado y sus documentos aparecen en el listado, desde donde puedo abrirlos o descargarlos con su nombre original.
- [ ] Dado un archivo que no es PDF/JPG/PNG o supera 10 MB, cuando intento adjuntarlo, entonces no se añade a la lista y veo el motivo.
- [ ] Dado un asiento recién guardado, cuando falla la subida de alguno de sus documentos, entonces el asiento sigue registrado, veo un aviso y puedo reintentar la subida sin crear otro asiento.
- [ ] Dado un asiento ya registrado con o sin documentos, cuando adjunto uno o varios archivos desde su fila del listado, entonces se añaden a ese asiento y aparecen junto a los anteriores sin crear otro asiento.

## Plan
- Guardar cada documento en disco, dentro de `backend/data/<CIF de la entidad>/<año del ejercicio>/`, con una ficha en base de datos ligada al asiento: nombre original, tipo real, tamaño, fecha y usuario que lo subió. La raíz es configurable con `DIRECTORIO_DATOS` y en base de datos se guarda la ruta relativa a ella.
- El alta del asiento no cambia: se crea primero y después se suben sus documentos a un endpoint del asiento, para poder reintentar solo los que fallen.
- Ese endpoint valida el tipo real y el tamaño (10 MB por archivo, 20 archivos y 50 MB por petición), exige tesorería o administración, y el listado de asientos devuelve sus documentos; la descarga queda abierta a cualquier usuario autenticado.
- En el formulario, un selector de archivos MUI con la lista de adjuntos y opción de quitarlos antes de guardar; en el listado, una columna con enlaces de descarga y un botón para adjuntar a cualquier asiento ya registrado.
- Tests de alta con documentos, rechazo por tipo real (firma del archivo) y tamaño, rechazo de archivos vacíos, límites por petición, descarga correcta, descarga cruzada entre asientos, idempotencia de reintentos, adjuntar a un asiento que ya tiene documentos y 403 de solo lectura al subir.

## Fuera de alcance
- Eliminar o sustituir documentos (eso es la #16).
- Previsualización dentro de la aplicación: el archivo se abre o se descarga.
- Límite de número de documentos por asiento, miniaturas, OCR o búsqueda por contenido.
- Cualquier ajuste de la matriz de permisos más allá de lo indicado (eso es la #17/#6).

## Sugerencias (a tu criterio)
- La página de asientos ya mezcla formulario y listado en un solo componente de unas 300 líneas; al añadir adjuntos en ambos lados, valorar extraer un componente de documentos reutilizable. Solo si al implementarlo ves que la página se vuelve difícil de seguir.
