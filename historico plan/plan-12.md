## Historia
Como tesorero/a, quiero poder utilizar las cuentas dadas de alta en el cuadro de cuentas base compartido al registrar movimientos, para usarlas inmediatamente en cualquier entidad.

## Criterios de aceptación
- [ ] Dado que soy tesorero/a y he seleccionado una entidad y un ejercicio, cuando abro el selector de cuentas en el formulario de nuevo asiento, entonces veo tanto las cuentas de esa entidad como las cuentas del cuadro de cuentas base compartido.
- [ ] Dado que selecciono una cuenta del cuadro de cuentas base compartido al crear un asiento, cuando guardo un asiento equilibrado, entonces se crea correctamente para esa entidad y ejercicio.
- [ ] Dado que utilizo una cuenta base compartida en un movimiento, cuando visualizo el asiento registrado, entonces el movimiento aparece correctamente asociado a esa cuenta base compartida.

## Plan
- Hacer que la lista de cuentas utilizada para registrar movimientos incluya las cuentas base compartidas junto a las cuentas propias de la entidad, para el contexto de la entidad seleccionada.
- Permitir la selección de cuentas base compartidas en el formulario de asientos sin necesidad de duplicarlas por entidad.
- Mantener sin cambios las reglas de permisos actuales para crear asientos (tesorero/a y administrador/a).
- Asegurar que el flujo de creación de asientos acepte valores de `cuenta_id` que pertenezcan al cuadro de cuentas base compartido.
- No restringir el uso de las cuentas base compartidas a una sola entidad.

## Fuera de alcance
- Crear, editar o desactivar cuentas desde la pantalla de asientos.
- Copiar cuentas base a entidades o asignarlas por entidad.
- Cambios en los permisos para visualizar el cuadro de cuentas base compartido.
- Importación bancaria (#3), revisión de borradores (#4) o el resto de #6.
- Cambios en la gestión de cuentas específicas de la entidad.

## Sugerencias (a tu criterio)
- Seguir el patrón existente de cómo la interfaz carga las cuentas: la unión de cuentas base + cuentas de entidad debe estar disponible en el mismo selector, sin inventar un nuevo flujo para el usuario.
- Si el backend actualmente filtra las cuentas estrictamente por `entidad_id`, considerar ampliar esa consulta para incluir también las cuentas con `entidad_id` NULL en el contexto de registro de movimientos. Solo hacerlo si encaja con los patrones existentes y no afecta a otros usos de ese listado.
