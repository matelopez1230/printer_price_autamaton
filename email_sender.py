# email_sender.py (igual que antes, solo la tabla)

import os
import logging
import smtplib
from email.message import EmailMessage
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

REMITENTE = os.getenv("REMITENTE")
CONTRASENIA = os.getenv("CONTRASENIA")
RECIPIENTES_RAW = os.getenv("RECIPIENTES", "")
RECIPIENTES_LIST = [email.strip() for email in RECIPIENTES_RAW.split(",") if email.strip()]


def enviar_correo(
    asunto: str,
    cuerpo_html: str,
    destinatarios: Optional[List[str]] = None,
    remitente: Optional[str] = None,
    contrasenia: Optional[str] = None,
) -> bool:
    if destinatarios is None:
        destinatarios = RECIPIENTES_LIST
        if not destinatarios:
            logger.error("No hay destinatarios configurados.")
            return False

    if remitente is None:
        remitente = REMITENTE
    if contrasenia is None:
        contrasenia = CONTRASENIA

    if not remitente or not contrasenia:
        logger.error("Faltan credenciales de correo.")
        return False

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = ", ".join(destinatarios)
    msg.set_content("Este correo requiere HTML.")
    msg.add_alternative(cuerpo_html, subtype="html")

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(remitente, contrasenia)
            server.send_message(msg)
        logger.info("Correo enviado.")
        return True
    except Exception as e:
        logger.error(f"Error al enviar: {e}")
        return False


def generar_cuerpo_html(resumen: dict) -> str:
    if resumen is None:
        resumen = {}
    fecha = resumen.get('fecha', 'Fecha no disponible')
    error = resumen.get('error', None)
    mensaje_error = f"""
        <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px;">
            <strong>⚠️ Error:</strong> {error}
        </div>
    """ if error else ""

    impresoras = resumen.get('impresoras', {})

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial; }}
            table {{ border-collapse: collapse; width: 80%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .ok {{ color: green; }}
            .fail {{ color: red; }}
        </style>
    </head>
    <body>
        <h2>  Reporte de Impresoras</h2>
        <p><strong>Fecha de ejecución:</strong> {fecha}</p>
        {mensaje_error}
        <h3>Resumen por impresora:</h3>
        <table>
            <tr><th>IP</th><th>Nombre</th><th>Sector</th><th>Contador</th><th>Variación</th><th>Estado</th></tr>
    """

    if impresoras:
        for ip, datos in impresoras.items():
            contador = datos.get('contador')
            diferencia = datos.get('diferencia')
            estado = datos.get('estado', 'Sin conexión')
            html += f"""
                <tr>
                    <td>{ip}</td>
                    <td>{datos.get('nombre', ip)}</td>
                    <td>{datos.get('sector', 'N/D')}</td>
                    <td>{contador if contador is not None else 'N/A'}</td>
                    <td>{diferencia if diferencia is not None else 'N/A'}</td>
                    <td>{estado}</td>
                </tr>
            """
    else:
        html += "<tr><td colspan='6'>No hay datos.</td></tr>"

    html += """
        </table>
        <p><em>Automático</em></p>
    </body>
    </html>
    """
    return html