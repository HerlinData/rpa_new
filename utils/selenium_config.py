# ====================================
# CONFIGURACIÓN DE SELENIUM
# ====================================
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from typing import Optional
from config.settings import DOWNLOADS_DIR, CHROME_OPTIONS

# User-Agent realista para evitar detección de bots
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

class SeleniumConfig:
    """
    Configurador de Selenium WebDriver.
    """

    def __init__(
        self,
        headless: Optional[bool] = None,
        download_dir: Optional[str] = None,
        chrome_driver_path: Optional[str] = None,
        user_agent: Optional[str] = None,
        window_size: tuple = (1920, 1080)
    ):
        """
        Inicializa la configuración de Selenium.

        Args:
            headless: Ejecutar sin interfaz gráfica (None = usar config.settings)
            download_dir: Directorio de descargas (None = usar config.settings)
            chrome_driver_path: Ruta al chromedriver (None = usar chromedriver en PATH)
            user_agent: User agent personalizado (None = usar default)
            window_size: Tamaño de ventana (ancho, alto)
        """
        # Usar configuración de settings.py o valores proporcionados
        self.headless = headless if headless is not None else CHROME_OPTIONS.get("headless", False)
        self.download_dir = Path(download_dir) if download_dir else DOWNLOADS_DIR
        self.chrome_driver_path = chrome_driver_path
        self.user_agent = user_agent if user_agent else DEFAULT_USER_AGENT
        self.window_size = window_size

        # Asegurar que exista el directorio de descargas
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _get_chrome_options(self) -> Options:
        """
        Configura y retorna las opciones de Chrome.
        """
        options = Options()

        # Configuración de descargas
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
        }
        options.add_experimental_option("prefs", prefs)

        # Modo headless (sin interfaz gráfica)
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        # Maximizar ventana o tamaño específico
        if not self.headless:
            options.add_argument("--start-maximized")
        else:
            options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")

        # User agent (siempre configurado para anti-detección)
        options.add_argument(f"user-agent={self.user_agent}")

        # Opciones de estabilidad y rendimiento
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Deshabilitar notificaciones
        options.add_argument("--disable-notifications")

        return options

    def create_driver(self) -> webdriver.Chrome:
        """
        Crea y retorna un WebDriver de Chrome configurado.
        """
        try:
            options = self._get_chrome_options()

            # Crear servicio si se especificó ruta a chromedriver
            if self.chrome_driver_path:
                service = Service(executable_path=self.chrome_driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # Usar chromedriver del PATH del sistema
                driver = webdriver.Chrome(options=options)

            # Configuraciones post-inicialización
            driver.implicitly_wait(10)  # Espera implícita de 10 segundos

            # Ejecutar script para evitar detección de automatización
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return driver

        except Exception as e:
            raise Exception(f"Error al crear WebDriver: {str(e)}")

    @staticmethod
    def create_default() -> webdriver.Chrome:
        """
        Método de conveniencia para crear un driver con configuración por defecto.
        """
        config = SeleniumConfig()
        return config.create_driver()