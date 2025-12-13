# ====================================
# HELPERS PARA SISTEMA DE ARCHIVOS
# ====================================
import time
import shutil
import tempfile
from pathlib import Path
import os

def renombrar_archivo(old_path, new_path, log_fn=print):
    """
    Renombra un archivo de old_path a new_path, con reintentos.
    Retorna True si exitoso, False si no.
    """
    for attempt in range(3):
        try:
            if os.path.exists(new_path):
                log_fn(f"Archivo '{new_path}' ya existe, será sobreescrito.")
                os.remove(new_path)
            
            os.rename(old_path, new_path)
            log_fn(f"Archivo renombrado de '{old_path}' a '{new_path}'")
            return True
        except Exception as e:
            log_fn(f"Error renombrando archivo (intento {attempt + 1}): {e}")
            time.sleep(1)
    log_fn(f"Fallo al renombrar '{old_path}' después de varios intentos.")
    return False

def limpiar_sesiones_antiguas(dias: int = 7):
    """
    Limpia directorios de sesiones de descarga ('rpa_downloads', x días) 
    """
    base_downloads = Path(tempfile.gettempdir()) / "rpa_downloads"

    if not base_downloads.exists():
        return 0

    tiempo_limite = time.time() - (dias * 86400)
    eliminados = 0

    for sesion_dir in base_downloads.iterdir():
        if sesion_dir.is_dir():
            # Verificar si es más antiguo que el límite
            try:
                if sesion_dir.stat().st_mtime < tiempo_limite:
                    shutil.rmtree(sesion_dir)
                    eliminados += 1
            except (OSError, FileNotFoundError):
                # Ignorar errores si el archivo fue eliminado por otro proceso
                pass

    return eliminados