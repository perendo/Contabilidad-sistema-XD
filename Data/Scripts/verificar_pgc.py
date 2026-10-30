"""Verifica el estado de las cuentas del ejercicio 2026.

Uso: desde backend/ con el venv raiz:
    ..\.venv\Scripts\python.exe ..\Data\Scripts\verificar_pgc.py
"""

import sqlite3

c = sqlite3.connect(r"H:\ContabilidadV2\backend\contabilidadv2.db")
print("total ejercicio 1:", c.execute("select count(*) from cuenta where ejercicio_id=1").fetchone()[0])
print("por nivel:", c.execute("select nivel, count(*) from cuenta where ejercicio_id=1 group by nivel order by nivel").fetchall())
print("duplicados:", c.execute("select codigo, count(*) from cuenta where ejercicio_id=1 group by codigo having count(*)>1").fetchall())
print("62x:")
for row in c.execute("select codigo, nombre from cuenta where ejercicio_id=1 and codigo like '62%' order by codigo"):
    print(" ", row)
print("padres nuevos:")
for row in c.execute("select codigo, nombre from cuenta where ejercicio_id=1 and codigo in ('65','72','74','77','620','624','626','644','660','707','720','740','742','743','744','748','749','778') order by codigo"):
    print(" ", row)
