# ====================================
# PASO 1: CONFIGURACIÓN CENTRALIZADA
# ====================================
import os
import tempfile
import socket
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import yaml

load_dotenv()

# ====================================
# RUTAS DEL PROYECTO
# ====================================
BASE_DIR = Path(__file__).parent.parent

# Directorio de descargas ÚNICO por ejecución
_hostname = socket.gethostname()
_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
_session_id = f"{_hostname}_{_timestamp}"

DOWNLOADS_DIR = Path(tempfile.gettempdir()) / "rpa_downloads" / _session_id

# Ruta base para guardar archivos procesados
BASE_OUTPUT_PATH = os.getenv("BASE_OUTPUT_PATH", "Z:/DESCARGA INFORMES")

# ====================================
# CREDENCIALES WEBS Y URL LOGIN
# ====================================
### SALESYS
SALESYS_USER = os.getenv("SALESYS_USER")
SALESYS_PASS = os.getenv("SALESYS_PASS")
SALESYS_URL = os.getenv("SALESYS_URL")
SALESYS_EXTENSION = os.getenv("SALESYS_EXTENSION")
SALESYS_DEVICE = os.getenv("SALESYS_DEVICE")

# Credenciales de base de datos
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# ====================================
# CONFIGURACIÓN DE CHROME
# ====================================
CHROME_OPTIONS = {"headless": False, "download_dir": str(DOWNLOADS_DIR),}

# ====================================
# CONFIGURACIÓN DE SESSION MANAGERS
# ====================================
MAX_LOGIN_ATTEMPTS = 3  # Número de intentos de login antes de fallar
LOGIN_TIMEOUT = 7  # Segundos de espera para elementos de login

# ====================================
# CONFIGURACIÓN DE LOGGING
# ====================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ====================================
# CONFIGURACIÓN DE FORMATOS Y NOMBRES
# ====================================
MESES_ES = { 1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",7: "Julio",
            8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

# ====================================
# CONFIGURACIÓN DE SCRAPERS (desde YAML)
# ====================================
ROUTES_PATH = BASE_DIR / "config" / "routes.yaml"

def load_routes():
    """Carga configuración completa de scrapers desde YAML"""
    if ROUTES_PATH.exists():
        with open(ROUTES_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        print(f"[WARNING] No se encontró {ROUTES_PATH}, funcionalidad limitada")
        return {}

ROUTES = load_routes()