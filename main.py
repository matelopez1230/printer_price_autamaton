# main.py
import logging
from pathlib import Path
from datetime import datetime

from config import IMPRESORAS, CONFIG, NOMBRES, SECTORES
from db_manager import init_db, tiene_datos, guardar_registro, obtener_ultimo_registro, obtener_resumen
from lector import obtener_contador
from email_sender import enviar_correo, generar_cuerpo_html

"""
------------------------INFORMACION IMPORTANTE------------------------
Este script realiza el monitoreo diario de las impresoras.
Requisitos previos:
- La base de datos SQLite debe contener datos históricos (ejecutar primero import_historical.py).
- Archivo de configuración impresoras.json con las impresoras a monitorear (copiar formato existente en impresoras.json). 


CASO DE PRIMERA IMPLEMENTACIÓN:
1. Ejecutar import_historical.py para cargar el historial desde el Excel a la base de datos SQLite.
2. Configurar impresoras.json con las impresoras a monitorear. (EN MI CASO NO HIZO FALTA)
2.2 Configurar config.py con los nombres y sectores de las impresoras.
2.3 Configurar .env con los datos del correo electrónico para enviar el resumen mensual.
3. Ejecutar main.py para realizar el monitoreo diario y enviar el correo con el resumen.
----------------------------------------------------------------------
"""

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Verificar si hay impresoras configuradas
    if not IMPRESORAS:
        logger.error("No hay impresoras configuradas. Verifica impresoras.json")
        exit(1)

    # Inicializar base de datos (crea la tabla si no existe)
    init_db()

    # Verificar que la base de datos no esté vacía
    if not tiene_datos():
        logger.error("La base de datos está vacía. Debes ejecutar primero 'python import_historical.py' para cargar el historial.")
        exit(1)

    # Fecha actual para el nuevo registro
    hoy = datetime.now()
    fecha_sql = hoy.strftime("%Y-%m-%d")
    fecha_excel = hoy.strftime("%d/%m/%Y")

    resumen = {
        'fecha': hoy.strftime("%d/%m/%Y %H:%M"),
        'impresoras': {},
        'error': None
    }

    # Procesar cada impresora
    for ip in CONFIG.keys():
        nombre = NOMBRES.get(ip, ip)
        sector = SECTORES.get(ip, "Sector no definido")
        logger.info(f"Procesando {nombre} ({ip})")

        # 1. Obtener contador actual
        contador_actual = obtener_contador(ip, CONFIG[ip])

        # 2. Obtener último registro de SQLite
        ultimo = obtener_ultimo_registro(ip)
        if ultimo:
            ultimo_contador = ultimo['contador']
            logger.info(f"Último contador en SQLite: {ultimo_contador} (fecha {ultimo['fecha']})")
        else:
            ultimo_contador = None
            logger.info("No hay historial en SQLite para esta IP.")

        # 3. Calcular diferencia (variación)
        if contador_actual is not None and ultimo_contador is not None:
            diferencia = contador_actual - ultimo_contador
        else:
            diferencia = None

        logger.info(f"Contador actual: {contador_actual}, Diferencia: {diferencia}")

        # 4. Guardar en SQLite el nuevo registro
        guardar_registro(ip, nombre, sector, fecha_sql, contador_actual, diferencia)

        # 5. Guardar en resumen para el correo
        resumen['impresoras'][ip] = {
            'nombre': nombre,
            'sector': sector,
            'contador': contador_actual,
            'diferencia': diferencia,
            'estado': 'OK' if contador_actual is not None else 'Sin conexión'
        }

    # Enviar correo
    asunto = f"Reporte de Impresoras - {hoy.strftime('%d/%m/%Y')}"
    cuerpo_html = generar_cuerpo_html(resumen)

    logger.info("Enviando correo...")
    exito = enviar_correo(asunto=asunto, cuerpo_html=cuerpo_html)

    if exito:
        logger.info("Proceso completado Exitosamente.")
    else:
        logger.error(" Error al enviar correo.")