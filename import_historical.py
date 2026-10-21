# import_historical.py
"""
Script independiente para importar el historial desde el archivo Excel
a la base de datos SQLite. Debe ejecutarse una sola vez (o cuando se
quiera reiniciar el historial).

Uso:
    python import_historical.py
    python import_historical.py "C:\\ruta\\al\\archivo.xlsx"
"""

import logging
import sys
from pathlib import Path

from db_manager import init_db, importar_desde_excel, obtener_ultima_fecha_por_ip
from config import NOMBRES, SECTORES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Por defecto: el Excel que está en la misma carpeta que este script
RUTA_POR_DEFECTO = Path(__file__).resolve().parent / "Relevamiento_impresoras_vigente.xlsx"


def resolver_ruta_excel() -> Path:
    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1]).expanduser()
    else:
        ruta = RUTA_POR_DEFECTO
    return ruta


if __name__ == "__main__":
    ruta_excel = resolver_ruta_excel()

    if not ruta_excel.exists():
        logger.error(f"No se encontró el archivo Excel: {ruta_excel}")
        logger.error(f"Ruta absoluta resuelta: {ruta_excel.resolve()}")
        logger.error("Opciones:")
        logger.error("  1) Copiá 'Relevamiento_impresoras_vigente.xlsx' a la carpeta del programa.")
        logger.error("  2) Pasá la ruta como argumento, por ejemplo:")
        logger.error('     python import_historical.py "C:\\Users\\mcescato\\Desktop\\Relevamiento_impresoras_vigente.xlsx"')
        sys.exit(1)

    logger.info(f"Usando Excel: {ruta_excel.resolve()}")

    init_db()

    logger.info("Iniciando importación desde Excel...")
    total = importar_desde_excel(ruta_excel)

    if total == 0:
        logger.error("No se importó ningún registro. Verifica el archivo y la configuración.")
        sys.exit(1)

    logger.info(f"Importación completada: {total} registros insertados.")

    ultimas_fechas = obtener_ultima_fecha_por_ip()
    logger.info("Resumen de últimos controles por impresora:")
    for ip, fecha in ultimas_fechas.items():
        nombre = NOMBRES.get(ip, ip)
        sector = SECTORES.get(ip, "Sector no definido")
        print(f"  {ip} ({nombre}) - Último control: {fecha} - Sector: {sector}")