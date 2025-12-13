# ====================================
# HELPERS PARA SISTEMA DE ARCHIVOS
# ====================================
import time
import shutil
import tempfile
from pathlib import Path

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