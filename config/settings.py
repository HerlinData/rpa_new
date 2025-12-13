# ====================================
# PASO 1: CONFIGURACIÓN CENTRALIZADA
# ====================================
import os
import tempfile
import socket
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
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

# ====================================
# CREDENCIALES WEBS Y URL LOGIN
# ====================================
### SALESYS
SALESYS_USER = os.getenv("SALESYS_USER")
SALESYS_PASS = os.getenv("SALESYS_PASS")
SALESYS_URL = os.getenv("SALESYS_URL", "http://amgclaro.touscorp.com/SaleSys/index.php/config")

### GENESYS
GENESYS_USER = os.getenv("GENESYS_USER")
GENESYS_PASS = os.getenv("GENESYS_PASS")
GENESYS_URL = os.getenv("GENESYS_URL", "https://genesys.example.com/login")

# ====================================
# FORM URL de cada reporte
# ====================================
### SALESYS
SALESYS_ESTADO_AGENTE_V2_FORM_URL = os.getenv("SALESYS_ESTADO_AGENTE_V2_FORM_URL", "http://amgclaro.touscorp.com/SaleSys/index.php/newstylereports/report_?id=259")
SALESYS_RGA_FORM_URL = os.getenv("SALESYS_RGA_FORM_URL", "http://amgclaro.touscorp.com/SaleSys/index.php/generaldeatencionesreport/form")

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
LOGIN_TIMEOUT = 15  # Segundos de espera para elementos de login

# ====================================
# CONFIGURACIÓN DE LOGGING
# ====================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"