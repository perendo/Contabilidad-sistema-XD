## Historia
Como tesorero/a, quiero consultar el cuadro de cuentas base compartido del PGC español hasta 3 dígitos, para ver las cuentas estándar disponibles para todas las entidades.

## Criterios de aceptación
- [x] Dado que he iniciado sesión como tesorero/a, cuando abro el cuadro de cuentas base compartido, entonces veo la lista de cuentas del PGC español con códigos de hasta 3 dígitos.
- [x] Dado que se muestra la lista, cuando consulto una entrada, entonces se visualiza al menos el código de la cuenta (hasta 3 dígitos) y su nombre o descripción.
- [x] Dado que el cuadro de cuentas base compartido está definido en el sistema, cuando lo consulto, entonces veo las cuentas del PGC español hasta 3 dígitos disponibles para todas las entidades.

## Plan
- **Identificar el alcance:** Diferenciar el cuadro de cuentas base compartido de las cuentas específicas de cada entidad.
- **Habilitar la consulta:** Permitir que el tesorero/a pueda acceder y consultar el listado del cuadro de cuentas base compartido.
- **Exponer los datos:** Mostrar las cuentas del PGC hasta 3 dígitos con su código, nombre y, en su caso, descripción.
- **Mantenerlo en solo lectura:** Limitar esta historia únicamente a la consulta, sin altas, ediciones ni eliminaciones.
- **Integrarlo con lo existente:** Aprovechar la estructura y los patrones ya presentes en la aplicación, sin rediseñar partes ajenas.

## Fuera de alcance
- Dar de alta o editar cuentas en el cuadro de cuentas base compartido (corresponde a la #11).
- Utilizar las cuentas del cuadro de cuentas base compartido al registrar movimientos (corresponde a la #12).
- Implementar la matriz de permisos completa (#6), más allá de lo estrictamente necesario para esta consulta.
- Realizar cambios en la gestión de cuentas por entidad, a menos que sea estrictamente necesario para distinguir entre cuentas compartidas y de entidad.

## Sugerencias (a tu criterio)
- **Distinguir cuentas compartidas y por entidad:** Dado que el modelo actual de `Cuenta` cuenta con `entidad_id`, puede ser necesario un mecanismo para identificar las cuentas compartidas (por ejemplo, la ausencia de `entidad_id` o un indicador específico). Esto resulta relevante para las historias futuras (#11 y #12).
- **Reutilizar patrones existentes:** Si ya existen vistas de listado en la interfaz (como la de entidades), seguir ese mismo patrón para mantener la coherencia con MUI y el estándar de Material Design.

## Resultado
Completada y verificada manualmente en el navegador el 2026-10-27.
- **API:** `GET /api/v1/cuentas/base`, en solo lectura y limitada a tesorería y administración.
- **Datos:** 421 cuentas del PGC (RD 1514/2007, 3 dígitos) sembradas desde `backend/app/db/pgc.py`.
- **Interfaz:** ruta `/cuentas-base` y entrada «Cuadro de cuentas» en el menú.
- **Pruebas:** 47/47 en el backend; build del frontend correcto.