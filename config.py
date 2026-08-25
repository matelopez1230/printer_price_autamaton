# config.py
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).parent / "impresoras.json"

def cargar_configuracion():
    """Carga la configuración de impresoras desde el archivo JSON."""
    if not CONFIG_FILE.exists():
        logger.error(f"Archivo de configuración {CONFIG_FILE} no encontrado.")
        return [], {}, {}

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear {CONFIG_FILE}: {e}")
        return [], {}, {}

    impresoras = data.get('impresoras', [])
    config_dict = {imp['ip']: {'ruta': imp['ruta'], 'metodo': imp['metodo']} for imp in impresoras}
    nombres = {imp['ip']: imp['nombre'] for imp in impresoras}
    sectores = {imp['ip']: imp['sector'] for imp in impresoras}

    logger.info(f"Cargadas {len(impresoras)} impresoras desde {CONFIG_FILE}")
    return impresoras, config_dict, nombres, sectores

# Cargar configuración al importar el módulo
IMPRESORAS, CONFIG, NOMBRES, SECTORES = cargar_configuracion()