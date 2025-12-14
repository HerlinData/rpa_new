# ====================================
# SELENIUM DRIVER PERSONALIZADO
# ====================================
# Clase que hereda de webdriver.Chrome y agrega funcionalidades de scraping
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path
from typing import Optional
import logging
import os
import time
from config.settings import DOWNLOADS_DIR, CHROME_OPTIONS


# User-Agent realista para evitar detección de bots
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

class SeleniumDriver(webdriver.Chrome):
    """
    WebDriver de Chrome personalizado con funcionalidades de scraping integradas.

    Hereda de webdriver.Chrome y agrega métodos útiles para web scraping:
    - Configuración automática de descargas
    - Esperas inteligentes
    - Gestión de descargas con CDP
    - Anti-detección

    Uso:
        driver = SeleniumDriver(headless=True)
        driver.get("https://example.com")
        driver.click(By.ID, "btn-login")
        archivo = driver.esperar_descarga(extension=".xlsx")
        driver.quit()
    """

    def __init__(
        self,
        headless: Optional[bool] = None,
        download_dir: Optional[str] = None,
        chrome_driver_path: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Inicializa el driver de Chrome con configuración optimizada para scraping.
        """
        # Configuración
        self.headless = headless if headless is not None else CHROME_OPTIONS.get("headless", False)
        self.download_dir = Path(download_dir) if download_dir else DOWNLOADS_DIR
        self.chrome_driver_path = chrome_driver_path
        self.user_agent = user_agent if user_agent else DEFAULT_USER_AGENT

        # Asegurar que existe el directorio de descargas
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Silenciar logs
        self._silenciar_logs()

        # Configurar opciones de Chrome
        options = self._get_chrome_options()

        # Configurar servicio
        service = self._get_service()

        # Inicializar Chrome con las opciones configuradas
        super().__init__(service=service, options=options)

        # Configuraciones post-inicialización
        self._post_init()

    def _silenciar_logs(self):
        """Silencia logs de Selenium y WebDriver Manager."""
        logging.getLogger('selenium').setLevel(logging.CRITICAL)
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)
        logging.getLogger('WDM').setLevel(logging.CRITICAL)
        os.environ['WDM_LOG'] = '0'
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

    def _get_chrome_options(self) -> Options:
        """Configura y retorna las opciones de Chrome."""
        options = Options()

        # Configuración de descargas (estricta para evitar rutas erróneas)
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "download_restrictions": 0,
        }
        options.add_experimental_option("prefs", prefs)

        # Silenciar logs de Chrome
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_argument('--disable-logging')

        # Modo headless
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        # User agent y opciones de estabilidad
        options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-notifications")

        return options

    def _get_service(self) -> Service:
        """Configura y retorna el servicio de ChromeDriver."""
        service_args = {'log_output': os.devnull}

        if self.chrome_driver_path:
            return Service(executable_path=self.chrome_driver_path, **service_args)
        else:
            return Service(**service_args)

    def _post_init(self):
        """Configuraciones post-inicialización del driver."""
        # Anti-detección: Ocultar que es Selenium
        self.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Habilitar Chrome DevTools Protocol (CDP) para gestión de descargas
        self.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(self.download_dir.absolute())
        })

    # ====================================
    # CONTEXT MANAGER (with statement)
    # ====================================

    def __enter__(self):
        """Permite usar SeleniumDriver con 'with' statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra el navegador automáticamente al salir del contexto."""
        self.quit()
        return False  # No suprimir excepciones

    # ====================================
    # MÉTODOS PERSONALIZADOS DE SCRAPING
    # ====================================

    def esperar(self, by: By, value: str, timeout: int = 10):
        """
        Espera a que un elemento sea clickeable y lo retorna.
        """
        return WebDriverWait(self, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def click(self, by: By, value: str, timeout: int = 10):
        """
        Espera a que un elemento sea clickeable y hace click.
        """
        elemento = self.esperar(by, value, timeout)
        elemento.click()

    def _obtener_directorio_descargas(self) -> Path:
        """Obtiene el directorio de descargas configurado usando CDP."""
        try:
            behavior = self.execute_cdp_cmd("Page.getDownloadBehavior", {})
            download_path = behavior.get("downloadPath")
            if download_path:
                return Path(download_path)
        except:
            pass

        return self.download_dir

    def limpiar_descargas(self):
        """
        Limpia la carpeta de descargas para asegurar detección confiable.
        Elimina archivos .csv, .xls, .xlsx pero mantiene .crdownload activos.
        """
        directorio = self._obtener_directorio_descargas()
        extensiones_a_limpiar = ['.csv', '.xls', '.xlsx', '.txt', '.pdf']

        for archivo in directorio.glob("*"):
            if archivo.is_file() and archivo.suffix in extensiones_a_limpiar:
                try:
                    archivo.unlink()
                except Exception:
                    pass  # Ignorar archivos en uso

    def esperar_descarga(self, timeout: int = 60, extension: str = None, limpiar_antes: bool = True) -> Path:
        """
        Espera a que se complete una descarga.

        Args:
            timeout: Tiempo máximo de espera en segundos
            extension: Extensión esperada del archivo (ej: '.csv')
            limpiar_antes: Si True, limpia la carpeta antes de esperar

        Returns:
            Path del archivo descargado
        """
        directorio = self._obtener_directorio_descargas()

        # Opcionalmente limpiar carpeta para detección confiable
        if limpiar_antes:
            self.limpiar_descargas()
            time.sleep(0.5)  # Breve pausa para que se complete la limpieza

        tiempo_inicio = time.time()

        while time.time() - tiempo_inicio < timeout:
            # Buscar archivos temporales de descarga
            archivos_temp = list(directorio.glob("*.crdownload")) + list(directorio.glob("*.tmp"))

            # Si NO hay archivos temporales, buscar el archivo descargado
            if not archivos_temp:
                archivos = list(directorio.glob("*"))

                # Filtrar por extensión si se especificó
                if extension:
                    archivos = [f for f in archivos if f.suffix == extension]

                # Filtrar solo archivos (no directorios)
                archivos = [f for f in archivos if f.is_file()]

                if archivos:
                    # Retornar el más reciente
                    archivo_descargado = max(archivos, key=lambda f: f.stat().st_mtime)
                    return archivo_descargado

            time.sleep(1.5)

        raise TimeoutError(f"Descarga no completada en {timeout} segundos")