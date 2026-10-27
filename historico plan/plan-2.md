## Historia
Como tesorero/a, quiero registrar una transacción equilibrada de ingresos o gastos con partida doble en la entidad y ejercicio seleccionados, para llevar al día los libros contables de esa entidad.

## Criterios de aceptación
- [x] Dado que estoy autenticado y he seleccionado una entidad y un ejercicio en el selector global de la cabecera, cuando accedo al diario o a la página de asientos, entonces el sistema habilita las operaciones contables para ese contexto.
- [x] Dado que estoy autenticado como tesorero/a (o administrador/a) y tengo una entidad y un ejercicio seleccionados, cuando creo un asiento con al menos dos apuntes (debe/haber) que sumen el mismo importe, entonces el sistema lo crea y le asigna un número de asiento secuencial por entidad y ejercicio.
- [x] Dado que el asiento no está cuadrado (debe != haber), tiene menos de dos apuntes o algún importe es 0 o negativo, cuando intento crearlo, entonces el sistema lo rechaza con un error y no crea el asiento.
- [x] Dado que estoy autenticado como solo lectura, cuando intento crear un asiento, entonces el sistema deniega el acceso (403).
- [x] Dado que no hay una entidad o un ejercicio seleccionados, cuando intento acceder al diario o a la creación de asientos, entonces el sistema impide la acción y me solicita que seleccione una entidad y un ejercicio desde el selector global de la cabecera.

## Plan
- **Contexto global (entidad + ejercicio):** Añadir un selector de entidad y ejercicio en la cabecera de `MarcoApp` tras el inicio de sesión. Este selector cargará los ejercicios correspondientes al cambiar de entidad, persistirá la selección en `sessionStorage` (o en el contexto de sesión de `sesion.tsx`), se preseleccionará automáticamente si solo existe una opción y limpiará su valor al cerrar sesión. 
- **Permisos de la API:** Requerir un usuario autenticado y permitir únicamente a tesorero/a y administrador/a crear asientos. Actualizar el endpoint para utilizar `usuario_actual` en lugar del primer usuario y aplicar la comprobación de rol correspondiente (se puede añadir una dependencia `solo_tesorero_o_admin` en `deps.py`).
- **Navegación y protección de rutas:** Añadir la sección "Diario / Asientos" al menú de `MarcoApp`, visible únicamente para tesorero/a y administrador/a y solo cuando exista una entidad y un ejercicio seleccionados. Añadir una protección a las rutas contables para redirigir o mostrar un aviso en caso de que falte el contexto.
- **Interfaz de registro:** Crear la página de asientos que obtenga `entidad_id` y `ejercicio_id` directamente del contexto global. Esta deberá incluir fecha, concepto, descripción y múltiples apuntes (cuenta, tipo debe/haber e importe), obteniendo las cuentas filtradas por la entidad seleccionada. Además, listar los asientos registrados para el contexto seleccionado.
- **Integración con el backend:** Mantener la validación de partida doble ya existente en los esquemas. Utilizar el usuario autenticado para asignar `registrado_por_id`. No será necesario modificar los endpoints, ya que estos seguirán recibiendo `entidad_id` y `ejercicio_id` tal como lo hacen actualmente.

## Fuera de alcance
- Importación de movimientos bancarios o generación de borradores (historias #3 y #4).
- Revisión de borradores o separación de responsabilidades más allá de la comprobación básica de rol para el registro (partes de la #6).
- Consultas o saldos más allá del listado básico de asientos (historia #5).
- Cambios a los permisos globales fuera de lo necesario para el registro de asientos.

## Sugerencias (a tu criterio)
- **Contexto centralizado:** Crear un contexto contable (ya sea extendiendo `sesion.tsx` o creando uno nuevo) con valores como `entidadSeleccionada`, `ejercicioSeleccionado`, sus setters y validaciones. Esto facilitará su reutilización en las historias #3, #4 y #5.
- **Mejoras en la cabecera:** Mostrar la selección actual como "Entidad: [Nombre] | Ejercicio: [Año]" para mayor claridad. En caso de no tener ninguna selección, mostrar un placeholder que invite al usuario a elegirla.
- **Protección reutilizable:** Crear un componente o guarda como `RequiereContextoContable` para evitar duplicar lógica en todas las rutas contables.
- **Reutilizar patrones existentes:** Seguir el estilo de `EntidadesPage` para los formularios y tablas con MUI, así como las comprobaciones de roles con `useSesion`. 
- **Validación cruzada:** Asegurarse de que, al cargar o cambiar de entidad, el ejercicio seleccionado siga siendo válido para esta. En caso contrario, seleccionar uno por defecto o limpiar la selección.

## Resultado
Cerrada el 2026-10-27. El registro equilibrado, la numeración secuencial por entidad/ejercicio, el rechazo de asientos inválidos y el 403 para solo lectura están cubiertos por `backend/tests/test_asientos_permisos.py`. El contexto global y el formulario están en `MarcoApp` y `AsientosPage`.
