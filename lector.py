# lector.py
# Lógica de conexión a las impresoras y extracción del contador

import re
import time
import logging
from collections import Counter
from typing import Optional, Dict, Any

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


# -------------------- Funciones de extracción --------------------

def extraer_contador_generico(html: str) -> Optional[int]:
    """
    Busca el contador de páginas en el HTML mediante múltiples patrones.
    Retorna un entero o None si no se encuentra.
    """
    patrones = [
        r'(?i)total\s*pages?\s*:?\s*(\d+)',
        r'(?i)páginas?\s*totales?\s*:?\s*(\d+)',
        r'(?i)page\s*count\s*:?\s*(\d+)',
        r'(?i)contador\s*de\s*páginas?\s*:?\s*(\d+)',
        r'(?i)impresas?\s*:?\s*(\d+)',
        r'(?i)printed\s*:?\s*(\d+)',
        r'(?i)counter\s*:?\s*(\d+)',
    ]
    for patron in patrones:
        match = re.search(patron, html, re.IGNORECASE)
        if match:
            return int(match.group(1))

    # Fallback: buscar números grandes (>= 5 dígitos) o el más frecuente
    numeros = re.findall(r'\b(\d{5,})\b', html)
    if numeros:
        contador = Counter(numeros)
        # Si algún número aparece al menos 2 veces, lo tomamos como el contador
        for num, freq in contador.most_common():
            if freq >= 2:
                return int(num)
        # Si no, tomamos el mayor
        return max(int(n) for n in numeros)

    return None


def extraer_contador_page_total(html: str) -> Optional[int]:
    """
    Extrae el contador específico para las páginas RICOH (Page Total).
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Estrategia 1: buscar fila con "Page Total"
    for tr in soup.find_all('tr'):
        celdas = tr.find_all('td')
        if len(celdas) >= 3:
            for celda in celdas:
                if 'Page Total' in celda.get_text():
                    texto_num = celdas[2].get_text(strip=True)
                    match = re.search(r'\d+', texto_num)
                    if match:
                        valor = int(match.group(0))
                        # Descartar 320 y números menores a 1000 (pueden ser falsos)
                        if valor != 320 and valor >= 1000:
                            return valor
                    break

    # Estrategia 2: buscar <td nowrap width="100%">
    for td in soup.find_all('td', attrs={'nowrap': True, 'width': '100%'}):
        texto = td.get_text(strip=True)
        match = re.search(r'\b(\d{4,})\b', texto)
        if match:
            valor = int(match.group(1))
            if valor != 320:
                return valor

    # Fallback al genérico
    return extraer_contador_generico(html)


# -------------------- Función principal de lectura --------------------

def obtener_contador(ip: str, config: Dict[str, Any]) -> Optional[int]:
    """
    Realiza la petición HTTP a la impresora con reintentos y extrae el contador.
    Retorna un entero o None en caso de fallo.
    """
    url = f"http://{ip}{config['ruta']}"
    metodo = config.get('metodo', 'generico')
    timeout = 15
    max_retries = 3

    for intento in range(1, max_retries + 1):
        try:
            logger.debug(f"Intentando {url} (intento {intento}/{max_retries})")
            respuesta = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
            respuesta.raise_for_status()
            html = respuesta.text
            break  # Éxito, salimos del bucle
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"Error en intento {intento} para {ip}: {e}")
            if intento == max_retries:
                logger.error(f"Fallo definitivo para {ip} después de {max_retries} intentos")
                return None
            # Espera exponencial: 2, 4, 8 segundos
            time.sleep(2 ** intento)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error inesperado en {ip}: {e}")
            return None

    # Extracción según método
    if metodo == "page_total":
        contador = extraer_contador_page_total(html)
    elif metodo == "contador_paginas":
        # Similar a page_total pero con patrón específico, usamos genérico
        contador = extraer_contador_generico(html)
    else:  # generico
        contador = extraer_contador_generico(html)

    if contador is None:
        logger.warning(f"No se pudo extraer contador de {ip}")
    else:
        logger.info(f"Contador obtenido para {ip}: {contador}")
    return contador