# ====================================
# PASO 1: CONFIGURACIÓN CENTRALIZADA
# ====================================
# Este archivo centraliza todas las configuraciones del proyecto
# Evita hardcodear credenciales y rutas en el código

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ====================================
# RUTAS DEL PROYECTO
# ====================================
# TODO: Ajusta estas rutas según tu proyecto
BASE_DIR = Path(__file__).parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
LOGS_DIR = BASE_DIR / "logs"
TEMP_DIR = BASE_DIR / "temp"


# ====================================
# CREDENCIALES (desde .env)
# ====================================
# TODO: Crear archivo .env con estas variables
# Ejemplo .env:
# SALESYS_USER=tu_usuario
# SALESYS_PASS=tu_password
# DB_SERVER=servidor
# DB_NAME=base_datos

# Credenciales de plataformas
SALESYS_USER = os.getenv("SALESYS_USER")
SALESYS_PASS = os.getenv("SALESYS_PASS")

GENESYS_USER = os.getenv("GENESYS_USER")
GENESYS_PASS = os.getenv("GENESYS_PASS")

# Credenciales de base de datos
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


# ====================================
# CONFIGURACIÓN DE CHROME
# ====================================
CHROME_OPTIONS = {
    "headless": False,  # Cambiar a True para ejecución sin interfaz
    "download_dir": str(DOWNLOADS_DIR),
}


# ====================================
# CONFIGURACIÓN DE LOGGING
# ====================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
