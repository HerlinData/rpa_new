# ====================================
# PASO 3: SCRAPER BASE (Nivel 2 POO)
# ====================================

from abc import ABC, abstractmethod
from pathlib import Path
from utils import SeleniumDriver


class BaseScraper(ABC):
    """
    Clase base para todos los scrapers.

    Flujo común (Template Method):
        1. configurar_driver()
        2. login()
        3. navegar_a_reporte()
        4. descargar_archivo()
        5. cerrar()
    """

    def __init__(self, platform_name: str):
        """
        Inicializa el scraper.
        """
        self.platform_name = platform_name
        self.driver = None

    # ====================================
    # MÉTODO PRINCIPAL (Template Method)
    # ====================================
    def ejecutar(self, **kwargs):
        """
        Ejecuta el flujo completo del scraper.
        Maneja la configuración y limpieza.
        El flujo principal de trabajo se delega a _run_main_flow.
        """
        try:
            print(f"[{self.platform_name}] Iniciando scraper...")
            self.configurar_driver()
            self.login()
            
            self._run_main_flow(**kwargs)

            print(f"\n[{self.platform_name}] ✓ Proceso de scraper completado.")

        except Exception as e:
            print(f"[{self.platform_name}] ✗ Error crítico durante la ejecución: {e}")
            raise

        finally:
            self.cerrar()

    # ====================================
    # MÉTODOS CONCRETOS (con implementación)
    # ====================================
    def configurar_driver(self):
        """
        Configura Chrome WebDriver usando SeleniumDriver.
        """
        # La importación se hace aquí para evitar importaciones circulares
        # si SeleniumDriver necesitara algo de los scrapers en el futuro.
        from utils.selenium_driver import SeleniumDriver
        self.driver = SeleniumDriver()
        print(f"[{self.platform_name}] ✓ Navegador configurado y listo")

    def cerrar(self):
        """
        Cierra el navegador si está abierto.
        """
        if self.driver:
            self.driver.quit()
            print(f"[{self.platform_name}] ✓ Navegador cerrado")

    # ====================================
    # MÉTODOS ABSTRACTOS (a implementar en subclases)
    # ====================================
    @abstractmethod
    def login(self):
        """
        TODO_EN SUBCLASE: Implementar lógica de login específica de cada plataforma
        """
        pass

    @abstractmethod
    def _run_main_flow(self, **kwargs):
        """
        Contiene el flujo principal del trabajo del scraper (ej. bucles, llamadas a descarga).
        Debe ser implementado por una clase base de plataforma (como BaseSalesys).
        """
        pass