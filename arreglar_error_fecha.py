import sqlite3

DB = r"\\srvdc01\Sistemas\Automatizacion Impresoraas\Impresoras\programa_ordenado\contadores.db"
COLUMNA_FECHA = "fecha"   # <-- CAMBIÁ ESTO por el nombre real

con = sqlite3.connect(DB)
cur = con.cursor()

# 1) Mostrar el esquema para confirmar
cur.execute("PRAGMA table_info(registros)")
print("Columnas de registros:")
for c in cur.fetchall():
    print(f"   {c[1]}  ({c[2]})")

# 2) Contar filas a borrar
cur.execute(f"SELECT COUNT(*) FROM registros WHERE date({COLUMNA_FECHA}) = ?", ("2026-10-20",))
print("Filas a borrar:", cur.fetchone()[0])

# 3) Borrar en transacción
cur.execute("BEGIN")
cur.execute(f"DELETE FROM registros WHERE date({COLUMNA_FECHA}) = ?", ("2026-10-20",))
print("Borradas:", cur.rowcount)
con.commit()

# 4) Verificar
cur.execute(f"SELECT COUNT(*) FROM registros WHERE date({COLUMNA_FECHA}) = ?", ("2026-10-20",))
print("Quedan con esa fecha:", cur.fetchone()[0])

con.close()