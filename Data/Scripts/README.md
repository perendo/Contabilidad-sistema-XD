# Scripts de carga del plan contable (parroquia)

Plantilla de cuentas de la parroquia cargada en el ejercicio 2026 de "Obispado de Getafe"
(empresa 1). No modifica el PGC base (`backend/app/pgc.py`); solo añade cuentas de usuario.

## Ficheros

| Fichero | Qué hace |
|---|---|
| `cargar_pgc.py` | Crea los 18 padres que faltan sobre el PGC base (nivel 2/3) y las 85 subcuentas de 6 dígitos (nivel 4). Idempotente: omite los códigos que ya existan. |
| `verificar_pgc.py` | Verifica el estado de las cuentas del ejercicio 2026 (total, por nivel, duplicados). |

## Uso

Desde `backend/` con el venv raíz:

```powershell
# Cargar la plantilla (si aún no está cargada)
..\.venv\Scripts\python.exe ..\Data\Scripts\cargar_pgc.py

# Verificar
..\.venv\Scripts\python.exe ..\Data\Scripts\verificar_pgc.py
```

## Estado actual

- Ejercicio 1 (empresa 1, 2026): 206 cuentas = 103 PGC base + 103 de la plantilla.
- Desduplicaciones aplicadas (columna "Concepto 2" de la plantilla):
  - `620100` Cáritas — ALEJANDRO / `620101` Cáritas — OSCAR
  - `628200` / `628201` / `628202` Electricidad
  - `660000` / `662000` Gastos Financieros
- `600`/`601` conservan su nombre PGC (la API no permite renombrar cuentas).
