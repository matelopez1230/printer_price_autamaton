# 📊 Sistema de Relevamiento de Impresoras en Red

Sistema automatizado para relevar contadores de impresoras, almacenar historial en SQLite, sincronizar con Excel y enviar reportes por correo electrónico.

---

## 🚀 Características

- Lectura de contadores desde impresoras vía HTTP (soporta múltiples modelos).
- Almacenamiento persistente en SQLite con cálculo automático de diferencias.
- Sincronización bidireccional con Excel (importa histórico y agrega nuevas filas).
- Envío de reportes por correo electrónico (solo tabla HTML, sin adjuntos).
- Configuración segura mediante archivo `.env` (credenciales y lista de impresoras).
- Múltiples destinatarios en el envío de correos.
- Logs detallados para depuración y seguimiento.

---

## 📁 Estructura del Proyecto  
\
├── .env # Variables de entorno (credenciales, impresoras)  
\
├── .gitignore # Archivos ignorados por Git  
\
├── README.md # Este archivo  
\
├── config.py # Configuración de impresoras (hardcodeada o desde .env)  
\
├── lector.py # Lógica de conexión HTTP y extracción de contadores  
\
├── db_manager.py # Operaciones con SQLite (guardar, leer, sincronizar)  
\
├── excel_actualizador.py # Orquestador: sincroniza Excel ↔ SQLite y escribe nuevas filas  
\
├── email_sender.py # Envío de correos con plantilla HTML  
\
├── main.py # Punto de entrada principal  
\
├── contadores.db # Base de datos SQLite (se crea automáticamente)  
\
└── requirements.txt # Dependencias del proyecto



---

## 🔧 Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

---

## 📦 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/relevamiento-impresoras.git
   cd relevamiento-impresoras


   python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt


# Credenciales de correo
REMITENTE=tu-correo@dominio.com
CONTRASENIA=tu-contraseña
RECIPIENTES=destinatario1@dominio.com, destinatario2@dominio.com

# Configuración de impresoras (JSON)
IMPRESORAS_JSON={
    "192.168.1.100": {
        "ruta": "/path/to/counter",
        "metodo": "generico",
        "nombre": "Impresora Oficina 1",
        "sector": "Administracion"
    },
    "192.168.1.101": {
        "ruta": "/counter.asp?Lang=en-us",
        "metodo": "page_total",
        "nombre": "Impresora Oficina 2",
        "sector": "RRHH"
    }
}
