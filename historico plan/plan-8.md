# Plan de la #8 — Alta de usuario con rol

Refinado el 2026-10-26. **Este fichero se borra cuando la #8 esté implementada y verificada.**

## Story
Como administrador/a, quiero dar de alta a un usuario con su nombre, email, contraseña inicial y rol, para que esa persona pueda entrar al sistema con los permisos que le correspondan.

## Acceptance criteria
- [ ] Given un administrador autenticado, when rellena nombre, email, contraseña y uno de los tres roles y guarda, then el usuario aparece en el listado con ese rol y puede iniciar sesión con ese email y esa contraseña.
- [ ] Given un usuario autenticado que no es administrador, when busca la gestión de usuarios, then no ve la sección en el menú y el sistema rechaza el alta sin crear nada.
- [ ] Given un administrador autenticado, when abre la sección de usuarios, then ve la lista con nombre, email, rol y si está activo.

## Plan
- Cifrar la contraseña al guardar y comprobar que el rol elegido existe: hoy se guarda en claro y el usuario recién creado nunca podría entrar.
- Reservar el alta y el listado a administradores, con rechazo en la API y la sección oculta en el menú para el resto.
- Añadir "Usuarios" al menú lateral, visible solo para administradores.
- Pantalla con formulario (nombre, email, contraseña y desplegable con los tres roles) y tabla de solo lectura.
- Refrescar la tabla tras guardar, con el rol que se le asignó.

## Out of scope
- Los avisos de email repetido y contraseña corta: son la #9, que va justo después.
- Editar, desactivar o borrar usuarios; cambiar o recuperar contraseñas.
- Aplicar el rol a lo que cada uno puede hacer: eso es la #6.
- Crear o renombrar roles, y el sembrado, que ya quedó en la #7.
- Buscar o paginar el listado.

## Suggestions (your call)
- La pantalla va a repetir el patrón de entidades (formulario en un panel y tabla debajo). Con dos casos todavía no extraería nada; si aparece una tercera pantalla igual, lo revisamos.

## Decisiones acordadas al refinar
- **El listado de usuarios lo ven solo los administradores**, igual que el alta.
- **La historia se parte en dos**: la #8 es el alta y el listado; la #9, ya en el backlog con `Requiere #8`, recoge los avisos de email repetido y contraseña demasiado corta (mínimo 8 caracteres).
- La aplicación es de escritorio: la sección nueva del menú no necesita adaptación a móvil.

## Notas del código actual
- `POST /api/v1/usuarios` guarda la contraseña **en claro** en `hashed_password` (`backend/app/api/v1/endpoints/usuarios.py:41`), así que un usuario creado así no puede entrar nunca. Es lo primero que hay que arreglar.
- Ese mismo endpoint **no comprueba el rol** (`usuarios.py:32`): cualquier usuario autenticado puede crear una cuenta de administrador. `GET /usuarios` tampoco lo comprueba.
- Ya existe el rechazo de email repetido con un 400, y `GET /roles` devuelve los tres roles con su identificador: es lo que alimenta el desplegable.
- `UsuarioCreate` pide `email`, `nombre_completo`, `password` y `rol_id`; `UsuarioRead` devuelve además `activo`, `creado_en` y el `rol` completo.
- En el frontend, el menú lateral ya existe (`frontend/src/components/MarcoApp.tsx`) y se amplía con una entrada más en `SECCIONES`.
- Pendiente al implementar: qué mensaje exacto ve el administrador si el sistema rechaza el alta por no tener permiso.
