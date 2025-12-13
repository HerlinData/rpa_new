# ====================================
# PASO 1: CONFIGURACIÓN CENTRALIZADA
# ====================================
# Este archivo centraliza todas las configuraciones del proyecto
# Evita hardcodear credenciales y rutas en el código

import os
import tempfile
import socket
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (debe estar en la raíz del proyecto)
load_dotenv()

# ====================================
# RUTAS DEL PROYECTO
# ====================================
BASE_DIR = Path(__file__).parent.parent

# Directorio de descargas ÚNICO por ejecución
# Esto evita conflictos cuando múltiples equipos o scrapers se ejecutan simultáneamente
_hostname = socket.gethostname()
_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
_session_id = f"{_hostname}_{_timestamp}"

DOWNLOADS_DIR = Path(tempfile.gettempdir()) / "rpa_downloads" / _session_id


# ====================================
# FUNCIONES HELPER PARA DIRECTORIOS
# ====================================
def limpiar_sesiones_antiguas(dias: int = 7):
    """
    Limpia directorios de sesiones anteriores más antiguos que N días.
    """
    import time
    import shutil

    base_downloads = Path(tempfile.gettempdir()) / "rpa_downloads"

    if not base_downloads.exists():
        return 0

    tiempo_limite = time.time() - (dias * 86400)  # días a segundos
    eliminados = 0

    for sesion_dir in base_downloads.iterdir():
        if sesion_dir.is_dir():
            # Verificar si es más antiguo que el límite
            if sesion_dir.stat().st_mtime < tiempo_limite:
                try:
                    shutil.rmtree(sesion_dir)
                    eliminados += 1
                except Exception:
                    pass  # Ignorar errores (puede estar en uso)

    return eliminados


# Limpiar sesiones antiguas al cargar configuración (opcional, puedes comentar si no quieres)
# limpiar_sesiones_antiguas(dias=7)


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
SALESYS_URL = os.getenv("SALESYS_URL", "http://amgclaro.touscorp.com/SaleSys/index.php/config")

GENESYS_USER = os.getenv("GENESYS_USER")
GENESYS_PASS = os.getenv("GENESYS_PASS")
GENESYS_URL = os.getenv("GENESYS_URL", "https://genesys.example.com/login")

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
# CONFIGURACIÓN DE SESSION MANAGERS
# ====================================
MAX_LOGIN_ATTEMPTS = 3  # Número de intentos de login antes de fallar
LOGIN_TIMEOUT = 15  # Segundos de espera para elementos de login


# ====================================
# CONFIGURACIÓN DE LOGGING
# ====================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
