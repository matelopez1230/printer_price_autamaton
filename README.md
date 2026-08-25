 Relevamiento de Impresoras – Sistema de Monitoreo y Reporte
Sistema automatizado para relevar contadores de impresoras en red, almacenar historial en SQLite, sincronizar con Excel y enviar reportes por correo electrónico.

 Características:
Lectura de contadores desde impresoras vía HTTP (soporta Brother, RICOH y genéricas).

Almacenamiento persistente en SQLite con cálculo automático de diferencias.

Sincronización bidireccional con Excel (importa histórico y agrega nuevas filas).

Envío de reportes por correo electrónico (solo tabla HTML, sin adjuntos).

Configuración segura mediante archivo .env (credenciales y lista de impresoras).

Múltiples destinatarios en el envío de correos.

Logs detallados para depuración y seguimiento.

Estructura del Proyecto
text
relevamiento_impresoras/
├── .env                      # Variables de entorno (credenciales, impresoras)
├── .gitignore                # Archivos ignorados por Git
├── README.md                 # Este archivo
├── config.py                 # Configuración de impresoras (hardcodeada o desde .env)
├── lector.py                 # Lógica de conexión HTTP y extracción de contadores
├── db_manager.py             # Operaciones con SQLite (guardar, leer, sincronizar)
├── excel_actualizador.py     # Orquestador: sincroniza Excel ↔ SQLite y escribe nuevas filas
├── email_sender.py           # Envío de correos con plantilla HTML
├── main.py                   # Punto de entrada principal
├── contadores.db             # Base de datos SQLite (se crea automáticamente)
└── requirements.txt          # Dependencias del proyecto
🔧 Requisitos
Python 3.8 o superior

Dependencias listadas en requirements.txt

Instalación
Clona el repositorio:

bash
git clone https://github.com/tu-usuario/relevamiento-impresoras.git
cd relevamiento-impresoras
Crea y activa un entorno virtual (opcional pero recomendado):

bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
Instala las dependencias:

bash
pip install -r requirements.txt
Configura las variables de entorno en el archivo .env (ver sección siguiente).

⚙️ Configuración (.env)
Crea un archivo .env en la raíz del proyecto con el siguiente contenido:

env
# Credenciales de correo
REMITENTE=tu-correo@dominio.com
CONTRASENIA=tu-contraseña
RECIPIENTES=destinatario1@dominio.com, destinatario2@dominio.com

# Configuración de impresoras (JSON)
IMPRESORAS_JSON={
    "192.168.16.22": {
        "ruta": "/general/information.html?kind=item",
        "metodo": "contador_paginas",
        "nombre": "Brother MFC-L2720DW",
        "sector": "C.A.C"
    },
    "192.168.16.23": {
        "ruta": "/counter.asp?Lang=en-us",
        "metodo": "page_total",
        "nombre": "RICOH M320F",
        "sector": "Administracion"
    }
}
📌 Explicación de variables
Variable	Descripción
REMITENTE	Correo electrónico que envía el reporte.
CONTRASENIA	Contraseña del remitente (para SMTP de Office 365).
RECIPIENTES	Lista de destinatarios separados por comas.
IMPRESORAS_JSON	Configuración en JSON de cada impresora: IP, ruta, método de extracción, nombre y sector.
⚠️ Importante: El archivo .env no debe subirse a Git. Asegúrate de agregarlo a .gitignore.

🧠 Métodos de Extracción
Cada impresora puede usar uno de estos métodos:

page_total – Para impresoras RICOH (busca "Page Total" en el HTML).

contador_paginas – Para Brother (busca "Contador de páginas").

generico – Busca patrones comunes como "total pages", "counter", etc.

📂 Sincronización con Excel
El sistema puede importar el historial desde un archivo Excel existente y luego agregar nuevas filas automáticamente.

Ubicación del Excel: Por defecto, C:\Users\mcescato\Desktop\Relevamiento_impresoras_vigente.xlsx. Puedes cambiarlo en main.py.

Formato de la hoja: Debe llamarse "Contadores" y tener las columnas:

A: Fecha (formato dd/mm/yyyy)

B: Sector

C: Nombre de impresora

D: IP

E: Contador (número)

📧 Envío de Correo
El correo se envía usando SMTP de Office 365 (puerto 587, TLS).
El cuerpo del mensaje es HTML y muestra una tabla con:

IP

Nombre

Sector

Contador actual

Variación (diferencia desde el último registro)

Estado (OK / Sin conexión)

No se adjunta ningún archivo.

▶️ Ejecución
bash
python main.py
El programa:

Sincroniza SQLite con el Excel (si es la primera ejecución).

Obtiene los contadores de cada impresora configurada.

Calcula la diferencia con el último registro histórico.

Guarda los nuevos registros en SQLite.

Agrega una nueva fila al Excel.

Envía el reporte por correo a los destinatarios configurados.

🛠️ Dependencias (requirements.txt)
text
requests>=2.28.0
beautifulsoup4>=4.11.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
Instálalas con:

bash
pip install -r requirements.txt
🐛 Solución de Problemas Comunes
Problema	Solución
python-dotenv could not parse statement	Verifica que el .env no tenga espacios ni caracteres extraños. Asegúrate de que el JSON esté en una sola línea o bien formateado.
ModuleNotFoundError	Instala las dependencias con pip install -r requirements.txt.
No se escribe en Excel	Cierra el archivo Excel antes de ejecutar el script. Verifica permisos de escritura.
Error de autenticación al enviar correo	Revisa que REMITENTE y CONTRASENIA sean correctos. Si usas autenticación de dos factores, genera una contraseña de aplicación.
La diferencia siempre es N/A	Asegúrate de que exista al menos un registro previo en SQLite o en el Excel para esa IP.
