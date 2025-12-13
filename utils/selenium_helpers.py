# ====================================
# PASO 6: UTILIDADES (OPCIONAL)
# ====================================
# Funciones helper comunes para Selenium

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path
import time


def esperar_descarga(directorio: Path, timeout: int = 60) -> Path:
    """
    TODO: Espera a que se complete una descarga en el directorio.

    Args:
        directorio: Path del directorio de descargas
        timeout: Segundos máximos a esperar

    Returns:
        Path del archivo descargado

    Implementación sugerida:
    - Monitorear archivos .crdownload o .tmp
    - Esperar a que desaparezcan
    - Retornar el archivo más reciente
    """
    pass


def esperar_elemento(driver, by: By, value: str, timeout: int = 10):
    """
    TODO: Espera a que un elemento sea visible.

    Args:
        driver: WebDriver de Selenium
        by: Tipo de locator (By.ID, By.XPATH, etc.)
        value: Valor del locator
        timeout: Segundos máximos a esperar

    Returns:
        WebElement encontrado
    """
    pass


def click_safe(driver, by: By, value: str, timeout: int = 10):
    """
    TODO: Click seguro que espera a que el elemento sea clickeable.

    Args:
        driver: WebDriver de Selenium
        by: Tipo de locator
        value: Valor del locator
        timeout: Segundos máximos a esperar
    """
    pass


def limpiar_directorio_descargas(directorio: Path, extension: str = "*.xlsx"):
    """
    TODO: Limpia archivos antiguos del directorio de descargas.

    Args:
        directorio: Path del directorio
        extension: Patrón de archivos a eliminar
    """
    pass
