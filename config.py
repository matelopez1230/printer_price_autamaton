# config.py
# Configuración centralizada de impresoras y carga de variables de entorno

import os
from dotenv import load_dotenv

# Cargar variables desde .env (busca en el directorio actual y padres)
load_dotenv()

# ========== IMPRESORAS (configuración fija) ==========
CONFIG = {
    "192.168.16.22": {
        "ruta": "/general/information.html?kind=item",
        "metodo": "contador_paginas"
    },
    "192.168.16.23": {
        "ruta": "/counter.asp?Lang=en-us",
        "metodo": "page_total"
    },
    "192.168.16.190": {
        "ruta": "/",
        "metodo": "generico"
    },
    "192.168.16.21": {
        "ruta": "/counter.asp?Lang=en-us",
        "metodo": "page_total"
    },
    "192.168.15.153": {
        "ruta": "/counter.asp?Lang=en-us",
        "metodo": "page_total"
    },
    "192.168.14.150": {
        "ruta": "/",
        "metodo": "generico"
    }
}

NOMBRES = {
    "192.168.16.22": "Brother MFC-L2720DW",
    "192.168.16.23": "RICOH M320F",
    "192.168.16.190": "Brother DCP-7065DN",
    "192.168.16.21": "RICOH M320F",
    "192.168.15.153": "RICOH M320F",
    "192.168.14.150": "Brother MFC-7460DN"
}

SECTORES = {
    "192.168.16.22": "C.A.C",
    "192.168.16.23": "Administracion",
    "192.168.16.190": "Oficinas atras P.A.",
    "192.168.16.21": "RRHH",
    "192.168.15.153": "Remitos",
    "192.168.14.150": "Oficina P.B."
}

# ========== VARIABLES DE ENTORNO ==========
REMITENTE = os.getenv("REMITENTE")
CONTRASENIA = os.getenv("CONTRASENIA")
RECIPIENTES = os.getenv("RECIPIENTES")
RUTA_EXCEL = os.getenv("RUTA_EXCEL")

# Validar que las variables críticas estén definidas
if not all([REMITENTE, CONTRASENIA, RECIPIENTES, RUTA_EXCEL]):
    raise EnvironmentError("Faltan variables de entorno. Revisa el archivo .env")