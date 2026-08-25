# db_manager.py
# Almacenamiento y consultas en SQLite, con función de importación desde Excel

import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from config import CONFIG, NOMBRES, SECTORES

logger = logging.getLogger(__name__)

DB_FILE = "contadores.db"


def init_db():
    """Crea la tabla registros si no existe."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            nombre TEXT NOT NULL,
            sector TEXT NOT NULL,
            fecha TEXT NOT NULL,  -- YYYY-MM-DD
            contador INTEGER,
            diferencia INTEGER,
            estado TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Base de datos SQLite inicializada.")


def guardar_registro(ip: str, nombre: str, sector: str, fecha: str,
                     contador: Optional[int], diferencia: Optional[int]) -> None:
    """Inserta un registro en SQLite."""
    estado = "OK" if contador is not None else "Sin conexión"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO registros (ip, nombre, sector, fecha, contador, diferencia, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ip, nombre, sector, fecha, contador, diferencia, estado))
    conn.commit()
    conn.close()
    logger.info(f"Registro guardado: {ip} fecha {fecha} contador {contador} dif {diferencia}")


def obtener_ultimo_registro(ip: str) -> Optional[Dict[str, Any]]:
    """Devuelve el registro más reciente para una IP."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT fecha, contador, diferencia, estado
        FROM registros
        WHERE ip = ?
        ORDER BY fecha DESC
        LIMIT 1
    """, (ip,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'fecha': row[0],
            'contador': row[1],
            'diferencia': row[2],
            'estado': row[3]
        }
    return None


def obtener_todos_registros(ip: str) -> List[Dict[str, Any]]:
    """Devuelve todos los registros de una IP ordenados por fecha."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT fecha, contador, diferencia, estado
        FROM registros
        WHERE ip = ?
        ORDER BY fecha ASC
    """, (ip,))
    rows = c.fetchall()
    conn.close()
    return [{'fecha': r[0], 'contador': r[1], 'diferencia': r[2], 'estado': r[3]} for r in rows]


def importar_desde_excel(ruta_excel: Path, sobrescribir: bool = False) -> int:
    """
    Lee todas las filas del Excel (hoja 'Contadores') y las importa a SQLite.
    Si sobrescribir es True, borra todos los registros existentes antes de importar.
    Retorna el número de registros importados.
    """
    if not ruta_excel.exists():
        logger.error(f"El archivo {ruta_excel} no existe.")
        return 0

    try:
        wb = load_workbook(ruta_excel)
    except InvalidFileException as e:
        logger.error(f"Archivo Excel no válido: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error al cargar Excel: {e}")
        return 0

    # Buscar hoja 'Contadores'
    hoja_nombre = None
    for nombre in wb.sheetnames:
        if nombre.lower() == "contadores":
            hoja_nombre = nombre
            break
    if not hoja_nombre:
        logger.error("No se encontró la hoja 'Contadores'.")
        return 0

    ws = wb[hoja_nombre]
    logger.info(f"Importando desde hoja: {hoja_nombre}")

    # Columnas: A=fecha, B=sector, C=nombre, D=ip, E=contador
    col_fecha = 1
    col_sector = 2
    col_impresora = 3
    col_ip = 4
    col_contador = 5

    # Recopilar todos los registros por IP
    registros_por_ip = {}
    for fila in range(2, ws.max_row + 1):
        ip = ws.cell(fila, col_ip).value
        if not ip or ip not in CONFIG:
            continue
        fecha_celda = ws.cell(fila, col_fecha).value
        contador_celda = ws.cell(fila, col_contador).value

        # Convertir fecha a string YYYY-MM-DD
        if isinstance(fecha_celda, datetime):
            fecha_str = fecha_celda.strftime("%Y-%m-%d")
        elif isinstance(fecha_celda, str):
            try:
                fecha_dt = datetime.strptime(fecha_celda, "%d/%m/%Y")
                fecha_str = fecha_dt.strftime("%Y-%m-%d")
            except:
                continue
        else:
            continue

        # Convertir contador a int
        try:
            contador_int = int(contador_celda) if contador_celda is not None else None
        except:
            contador_int = None

        if contador_int is None:
            continue

        nombre = ws.cell(fila, col_impresora).value or NOMBRES.get(ip, ip)
        sector = ws.cell(fila, col_sector).value or SECTORES.get(ip, "Sector no definido")

        if ip not in registros_por_ip:
            registros_por_ip[ip] = {
                'nombre': nombre,
                'sector': sector,
                'registros': []
            }
        registros_por_ip[ip]['registros'].append((fecha_str, contador_int))

    # Inicializar base de datos
    init_db()

    if sobrescribir:
        # Borrar todos los registros existentes
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM registros")
        conn.commit()
        conn.close()
        logger.info("Base de datos limpiada (sobrescritura).")

    total_importados = 0
    for ip, data in registros_por_ip.items():
        # Ordenar registros por fecha
        registros = sorted(data['registros'], key=lambda x: x[0])
        ultimo_contador = None
        for fecha_str, contador in registros:
            # Verificar si ya existe este registro (misma IP y fecha)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id FROM registros WHERE ip = ? AND fecha = ?", (ip, fecha_str))
            existe = c.fetchone()
            conn.close()
            if existe and not sobrescribir:
                continue
            # Calcular diferencia
            if ultimo_contador is not None:
                diferencia = contador - ultimo_contador
            else:
                diferencia = None
            guardar_registro(ip, data['nombre'], data['sector'], fecha_str, contador, diferencia)
            ultimo_contador = contador
            total_importados += 1

    logger.info(f"Importados {total_importados} registros desde Excel a SQLite.")
    return total_importados


def actualizar_contadores() -> dict:
    """
    Función principal: para cada IP, obtiene el contador actual,
    calcula diferencia contra el último registro en SQLite,
    y guarda el nuevo registro.
    """
    from lector import obtener_contador  # import local para evitar dependencia circular

    init_db()
    hoy = datetime.now()
    fecha_sql = hoy.strftime("%Y-%m-%d")

    resumen = {
        'fecha': hoy.strftime("%d/%m/%Y %H:%M"),
        'impresoras': {},
        'error': None
    }

    for ip, config in CONFIG.items():
        nombre = NOMBRES.get(ip, ip)
        sector = SECTORES.get(ip, "Sector no definido")
        logger.info(f"Procesando {nombre} ({ip})")

        # Obtener contador actual
        contador_actual = obtener_contador(ip, config)

        # Obtener último registro de SQLite
        ultimo = obtener_ultimo_registro(ip)
        if ultimo:
            ultimo_contador = ultimo['contador']
            logger.info(f"Último contador en SQLite: {ultimo_contador} (fecha {ultimo['fecha']})")
        else:
            ultimo_contador = None
            logger.info("No hay historial en SQLite para esta IP.")

        # Calcular diferencia
        if contador_actual is not None and ultimo_contador is not None:
            diferencia = contador_actual - ultimo_contador
        else:
            diferencia = None

        logger.info(f"Contador actual: {contador_actual}, Diferencia: {diferencia}")

        # Guardar en SQLite
        guardar_registro(ip, nombre, sector, fecha_sql, contador_actual, diferencia)

        # Guardar en resumen
        resumen['impresoras'][ip] = {
            'nombre': nombre,
            'sector': sector,
            'contador': contador_actual,
            'diferencia': diferencia,
            'estado': 'OK' if contador_actual is not None else 'Sin conexión'
        }

    return resumen