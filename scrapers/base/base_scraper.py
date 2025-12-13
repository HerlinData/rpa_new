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
    def ejecutar(self) -> Path:
        """
        Ejecuta el flujo completo del scraper.
        """
        try:
            print(f"[{self.platform_name}] Iniciando scraper...")

            # 1. Configurar driver
            self.configurar_driver()

            # 2. Login
            self.login()

            # 3. Navegar al reporte
            self.navegar_a_reporte()

            # 4. Descargar archivo
            ruta_archivo = self.descargar_archivo()

            print(f"[{self.platform_name}] ✓ Scraper completado exitosamente")
            print(f"[{self.platform_name}] ✓ Archivo guardado en: {ruta_archivo}")
            return ruta_archivo

        except Exception as e:
            print(f"[{self.platform_name}] ✗ Error: {str(e)}")
            raise

        finally:
            # 5. Siempre cerrar driver
            self.cerrar()

    # ====================================
    # MÉTODOS CONCRETOS (con implementación)
    # ====================================
    def configurar_driver(self):
        """
        Configura Chrome WebDriver usando SeleniumDriver.
        """
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
    def navegar_a_reporte(self):
        """
        TODO_EN SUBCLASE: Navegar al reporte específico
        """
        pass

    @abstractmethod
    def descargar_archivo(self) -> Path:
        """
        TODO_EN SUBCLASE: Descargar el archivo de datos
        """
        pass