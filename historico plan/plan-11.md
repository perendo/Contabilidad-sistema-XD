## Historia
Como tesorero/a, quiero dar de alta una nueva cuenta hasta 8 dígitos en el cuadro de cuentas base compartido, para ampliarlo con las cuentas que necesito para mis operaciones.

## Criterios de aceptación
- [ ] Dado que estoy autenticado como tesorero/a o administrador/a, cuando doy de alta una cuenta base con un código numérico de hasta 8 dígitos que no exista en el cuadro de cuentas base compartido, entonces la cuenta se crea con `entidad_id` = NULL y aparece en `GET /cuentas/base`.
- [ ] Dado que ya existe una cuenta con ese código en el cuadro de cuentas base compartido, cuando intento darla de alta, entonces el sistema rechaza la creación e informa de que ya existe una cuenta base con ese código.
- [ ] Dado que estoy autenticado como solo lectura, cuando intento dar de alta una cuenta en el cuadro de cuentas base compartido, entonces el sistema devuelve un 403.

## Plan
- Permitir dar de alta cuentas en el cuadro de cuentas base compartido (`entidad_id` NULL), manteniendo sin cambios el flujo existente para cuentas vinculadas a una entidad.
- Exigir que las cuentas base utilicen un código numérico de hasta 8 dígitos y que sea único dentro del cuadro de cuentas base compartido (`entidad_id` IS NULL).
- Restringir la creación de cuentas base a tesorero/a o administrador/a (de forma coherente con los permisos ya aplicados a `GET /cuentas/base`).
- Reutilizar el concepto de "cuadro de cuentas base" ya existente en el modelo (`entidad_id` NULL = cuadro base compartido), sin introducir nuevas entidades ni grupos de cuentas.

## Fuera de alcance
- Modificar, desactivar o eliminar cuentas base.
- Crear cuentas para una entidad concreta (ya cubierto por el flujo existente).
- Permitir cuentas base con más de 8 dígitos o con códigos no numéricos.
- Importación masiva de cuentas base.
- Cualquier modificación a las cuentas semilladas del PGC hasta 3 dígitos.

## Sugerencias (a tu criterio)
- **Reutilizar la autorización existente:** Aplicar el mismo `solo_tesorero_o_admin` utilizado en `GET /cuentas/base` a la acción de creación de cuentas base para evitar duplicar la lógica de roles.
- **Ser explícito con el destino:** Ampliar `POST /cuentas` para admitir `entidad_id` null con las reglas más estrictas anteriores, o añadir un `POST /cuentas/base` específico. Cualquiera de las dos opciones que se ajuste mejor al estilo de API existente con el menor cambio será preferible.
