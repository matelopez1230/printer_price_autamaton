# main.py
import logging
from datetime import datetime
from pathlib import Path

from db_manager import actualizar_contadores, importar_desde_excel
from email_sender import enviar_correo, generar_cuerpo_html

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Opcional: si se desea importar desde Excel (por ejemplo, la primera vez)
    # Descomentar la siguiente línea y ejecutar una vez para cargar el historial.
    # ruta_excel = Path(r"C:\Users\mcescato\Desktop\Relevamiento_impresoras_vigente.xlsx")
    # importar_desde_excel(ruta_excel, sobrescribir=False)

    logger.info("Inicio de ejecución (usando SQLite)")
    resumen = actualizar_contadores()

    asunto = f"Reporte de Impresoras - {datetime.now().strftime('%d/%m/%Y')}"
    cuerpo_html = generar_cuerpo_html(resumen)

    logger.info("Enviando correo...")
    exito = enviar_correo(asunto=asunto, cuerpo_html=cuerpo_html)

    if exito:
        logger.info("✅ Proceso completado.")
    else:
        logger.error("❌ Error al enviar correo.")