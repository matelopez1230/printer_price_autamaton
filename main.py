# main.py
import logging
from pathlib import Path
from datetime import datetime

from config import IMPRESORAS, CONFIG, NOMBRES, SECTORES
from db_manager import init_db, tiene_datos, importar_desde_excel, guardar_registro, obtener_ultimo_registro, obtener_resumen
from lector import obtener_contador
from email_sender import enviar_correo, generar_cuerpo_html

"""
------------------------INFORMACION IMPORTANTE------------------------
Este script realiza las siguientes funciones:
1. Inicializa la base de datos SQLite si no existe.
2. Si la base de datos está vacía, importa los registros desde un archivo Excel.
3. Para cada impresora configurada, obtiene el contador actual desde la impresora.
4. Compara el contador actual con el último registro en SQLite para calcular la diferencia.
5. Guarda el nuevo registro en SQLite.
6. Genera un resumen de todos los registros y envía un correo electrónico con el reporte.
Requisitos:

- Archivo de configuración `impresoras.json` con las impresoras a monitorear.
    - En cada impresora hay un 'Metodo' que refiere a como esta configurado el sitio del que se obtiene la información de la cantidad de hojas usadas

- Archivo Excel con los registros históricos (solo para la importación inicial).
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

    # Ruta al archivo Excel (solo para importación inicial)
    ruta_excel = Path(r"C:\Users\mcescato\Desktop\Relevamiento_impresoras_vigente.xlsx")

    # Inicializar base de datos
    init_db()

    # Si la base de datos está vacía, importar desde Excel
    if not tiene_datos():
        logger.info("Base de datos vacía. Importando desde Excel...")
        importados = importar_desde_excel(ruta_excel)
        if importados == 0:
            logger.warning("No se importaron datos. Usando solo configuraciones actuales.")
    else:
        logger.info("SQLite ya contiene datos. No se importará el Excel.")

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

        # 3. Calcular diferencia
        if contador_actual is not None and ultimo_contador is not None:
            diferencia = contador_actual - ultimo_contador
        else:
            diferencia = None

        logger.info(f"Contador actual: {contador_actual}, Diferencia: {diferencia}")

        # 4. Guardar en SQLite
        guardar_registro(ip, nombre, sector, fecha_sql, contador_actual, diferencia)

        # 5. Guardar en resumen
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
        logger.info("✅ Proceso completado.")
    else:
        logger.error("❌ Error al enviar correo.")