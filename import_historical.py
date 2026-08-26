# import_historical.py
"""
Script independiente para importar el historial desde el archivo Excel
a la base de datos SQLite. Debe ejecutarse una sola vez (o cuando se
quiera reiniciar el historial).
"""

import logging
from pathlib import Path
from db_manager import init_db, importar_desde_excel, obtener_ultima_fecha_por_ip
from config import NOMBRES, SECTORES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Ruta al archivo Excel (ajústala si es necesario)
    ruta_excel = Path(r"PATH\TO\FILE")
    
    # Inicializar base de datos (crea la tabla si no existe)
    init_db()
    
    # Importar todos los registros del Excel
    logger.info("Iniciando importación desde Excel...")
    total = importar_desde_excel(ruta_excel)
    
    if total == 0:
        logger.error("No se importó ningún registro. Verifica el archivo y la configuración.")
        exit(1)
    
    logger.info(f"Importación completada: {total} registros insertados.")
    
    # Mostrar resumen de última fecha por IP
    ultimas_fechas = obtener_ultima_fecha_por_ip()
    logger.info("Resumen de últimos controles por impresora:")
    for ip, fecha in ultimas_fechas.items():
        nombre = NOMBRES.get(ip, ip)
        sector = SECTORES.get(ip, "Sector no definido")
        print(f"  {ip} ({nombre}) - Último control: {fecha} - Sector: {sector}")
