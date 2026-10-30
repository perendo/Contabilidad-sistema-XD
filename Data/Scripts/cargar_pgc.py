"""Carga la plantilla de cuentas de la parroquia en el ejercicio 2026 (Obispado de Getafe).

- Crea los 18 padres que faltan sobre el PGC base (nivel 2/3).
- Crea las 85 subcuentas de 6 digitos (nivel 4, convencion de la app).
- Idempotente: omite los codigos que ya existan.

Uso: desde backend/ con el venv raiz:
    ..\.venv\Scripts\python.exe ..\Data\Scripts\cargar_pgc.py
"""

from sqlmodel import Session, select

from app.db import engine
from app.models import Cuenta, Ejercicio

# (codigo, nombre) — nivel = len(codigo) si <= 3 digitos; si no, 4.
PADRES = [
    ("65", "Entregas Parroquiales"),
    ("72", "Aportaciones a recibir Com.Dioc."),
    ("74", "Aportaciones de los Fieles"),
    ("77", "Otros Ingresos"),
    ("620", "Activ. Asistenciales y Pastorales"),
    ("624", "Transportes"),
    ("626", "Servicios Bancar. (Comis. y Gastos)"),
    ("644", "Sueldos sacerdotes y religiosos"),
    ("660", "Gastos Financieros"),
    ("707", "Ingresos convivencias y cursillos"),
    ("720", "Aportaciones del Fondo Dioc."),
    ("740", "Subvenciones Entidades Públicas"),
    ("742", "Día de la Iglesia Diocesana"),
    ("743", "Donativos y Limosnas"),
    ("744", "Cuotas (remesas y traspasos bancos)"),
    ("748", "Entregas colectas otras instit."),
    ("749", "Cáritas parroquial"),
    ("778", "Ing. Extraordinarios"),
]

SUBCUENTAS = [
    ("600001", "Material venta: libros, obj.piadosos …"),
    ("600002", "Belén - Gastos generales"),
    ("600003", "Palmas Semana Santa"),
    ("600004", "Velas Veremundo"),
    ("601000", "Material Inventariable (imágenes, bancos,…)"),
    ("601001", "Mercado del Mueble"),
    ("620100", "Cáritas parroquial (Ayuda Social) - ALEJANDRO"),
    ("620101", "Cáritas parroquial (Ayuda Social) - OSCAR (JARDIN)"),
    ("620200", "Atenciones a los Fieles, Gastos Pastorales"),
    ("620202", "Convivencias y campamentos, cursillos…"),
    ("620203", "Jornada de infancia y Reyes"),
    ("620204", "Otras activ. Pastorales"),
    ("621000", "Alquier SDS"),
    ("622000", "Instalaciones PRESUR"),
    ("622001", "Megafonía (EGSON)"),
    ("622002", "Reparaciones ord. (mantenimiento)"),
    ("622003", "Ascensores FAIN"),
    ("622004", "BOMBAS BRUG (Manuel Gomez Marquez)"),
    ("622005", "PROWAL SL (Mantenimiento Tejado)"),
    ("622006", "Sistemas Contra Incendios"),
    ("622007", "Técnicas Áreas de la Construcción"),
    ("622008", "Ejezeta Trabajos En Altura"),
    ("622009", "Daikin - Aire Acondicionado"),
    ("622010", "Juan Andrés López Salazar - mantenimiento placas solares"),
    ("622100", "Reparaciones extraordinarias"),
    ("622200", "Limpieza"),
    ("622900", "Otros menores (jardinería)"),
    ("623200", "Pago Monitores"),
    ("624000", "Alquiler furgonetas, buses, etc…"),
    ("625000", "Seguros UMAS"),
    ("626000", "Servicios Bancar. (Comis. y Gastos)"),
    ("628000", "Agua"),
    ("628100", "Gas"),
    ("628200", "Electricidad"),
    ("628201", "Electricidad - SOLAR PROFIT MONTAJE PLACAS SOLARES"),
    ("628202", "Electricidad - Placas solares"),
    ("628300", "Combustibles (fuel oil, butano)"),
    ("628500", "Material para el culto (Liturgia) Ángel Gómez Pérez (antiguo Barroso)"),
    ("628501", "Flores"),
    ("628502", "Material de culto (Otros proveedores)"),
    ("628900", "Otros Suministros"),
    ("629100", "Viajes y Dietas"),
    ("629200", "Material oficina"),
    ("629220", "Fotocopias (Burocopy)"),
    ("629221", "Fotocopias (Siemens Renting)"),
    ("629330", "Teléfono, fax y correo"),
    ("629900", "Imprevistos (evitar usar)"),
    ("631000", "Tributos Ayuntamiento"),
    ("644000", "Sueldos sacerdotes y religiosos"),
    ("650000", "Entregas al Fondo Común Dioc.(10%)"),
    ("652000", "Entregas colectas Diócesis (cta. 742)"),
    ("653000", "Entregas colectas otras instit. (c. 748)"),
    ("660000", "Gastos Financieros"),
    ("662000", "Intereses de Deudas"),
    ("700001", "Libros, objetos piadosos…"),
    ("700002", "Belén"),
    ("700003", "Semana Santa y Palmas"),
    ("700004", "Velas"),
    ("700005", "Misas Mensajeros de la paz"),
    ("700901", "Funerarias / funerales"),
    ("700902", "Regalos y Atenciones"),
    ("700903", "Lotería"),
    ("700904", "Columbario"),
    ("700905", "Jornada infancia y reyes"),
    ("705010", "Tasas (Expedientes)"),
    ("705020", "Bautizos"),
    ("705021", "Primeras Comuniones"),
    ("705022", "Bodas"),
    ("705023", "Misas (Intenciones)"),
    ("705029", "Otros servicios parroq. (Confirmaciones)"),
    ("707000", "Ingresos convivencias y cursillos"),
    ("720000", "Aportaciones del Fondo Dioc."),
    ("740000", "Subvenciones Entidades Públicas"),
    ("742000", "Día de la Iglesia Diocesana"),
    ("742001", "Colectas S.Francisco Javier"),
    ("742010", "Seminario"),
    ("743001", "Donativos y Limosnas"),
    ("743002", "Donativos S.Cirilo y S.Metodio"),
    ("744000", "Cuotas (remesas y traspasos bancos)"),
    ("748001", "Manos Unidas. Campaña contral el hambre"),
    ("748004", "Cáritas"),
    ("748006", "Domund"),
    ("748011", "Santos Lugares"),
    ("749000", "Cáritas parroq.de Pinto (620100)"),
    ("778000", "Ing. Extraordinarios"),
]


def main() -> None:
    with Session(engine) as s:
        ej = s.exec(
            select(Ejercicio).where(Ejercicio.empresa_id == 1, Ejercicio.anio == 2026)
        ).first()
        if ej is None:
            raise SystemExit("No existe el ejercicio 2026 de la empresa 1")
        if ej.estado != "abierto":
            raise SystemExit(f"El ejercicio {ej.id} no está abierto")

        existentes = set(
            s.exec(select(Cuenta.codigo).where(Cuenta.ejercicio_id == ej.id))
        )
        nuevas, omitidas = [], []
        for codigo, nombre in PADRES + SUBCUENTAS:
            if codigo in existentes:
                omitidas.append(codigo)
                continue
            nivel = len(codigo) if len(codigo) <= 3 else 4
            nuevas.append(
                Cuenta(
                    ejercicio_id=ej.id, codigo=codigo, nombre=nombre, nivel=nivel
                )
            )
        if nuevas:
            s.add_all(nuevas)
            s.commit()
        print(f"Ejercicio {ej.id} (empresa 1, {ej.anio})")
        print(f"Creadas: {len(nuevas)} ({sum(1 for c, _ in PADRES if c not in existentes)} padres + "
              f"{sum(1 for c, _ in SUBCUENTAS if c not in existentes)} subcuentas)")
        if omitidas:
            print(f"Omitidas (ya existían): {', '.join(omitidas)}")


if __name__ == "__main__":
    main()
