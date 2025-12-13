# ====================================
# PASO 3: SCRAPER BASE (Nivel 2 POO)
# ====================================
# Clase base que define el flujo común de todos los scrapers
# Usa Template Method Pattern: define el esqueleto, las subclases implementan detalles

from abc import ABC, abstractmethod
from selenium import webdriver
import pandas as pd
from pathlib import Path
from utils.selenium_config import SeleniumConfig


class BaseScraper(ABC):
    """
    Clase base para todos los scrapers.

    Flujo común (Template Method):
        1. configurar_driver()
        2. login()
        3. navegar_a_reporte()
        4. descargar_archivo()
        5. procesar_datos()
        6. guardar_en_bd()
        7. cerrar()

    Las subclases solo implementan los métodos abstractos.
    """

    def __init__(self, platform_name: str):
        """
        Inicializa el scraper.

        Args:
            platform_name: Nombre de la plataforma (ej: "Salesys", "Genesys")
        """
        self.platform_name = platform_name
        self.driver = None
        self.df_resultado = None

    # ====================================
    # MÉTODO PRINCIPAL (Template Method)
    # ====================================
    def ejecutar(self) -> pd.DataFrame:
        """
        Ejecuta el flujo completo del scraper.
        Este método NO se sobreescribe en las subclases.

        Returns:
            DataFrame con datos procesados
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

            # 5. Procesar datos
            self.df_resultado = self.procesar_datos(ruta_archivo)

            # 6. Guardar en BD (opcional)
            if self.df_resultado is not None:
                self.guardar_en_bd(self.df_resultado)

            print(f"[{self.platform_name}] ✓ Scraper completado exitosamente")
            return self.df_resultado

        except Exception as e:
            print(f"[{self.platform_name}] ✗ Error: {str(e)}")
            raise

        finally:
            # 7. Siempre cerrar driver
            self.cerrar()

    # ====================================
    # MÉTODOS CONCRETOS (con implementación)
    # ====================================
    def configurar_driver(self):
        """
        Configura Chrome WebDriver usando SeleniumConfig.

        Las subclases pueden sobreescribir este método si necesitan
        configuraciones específicas de driver.
        """
        selenium_config = SeleniumConfig()
        self.driver = selenium_config.create_driver()
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
        TODO EN SUBCLASE: Implementar lógica de login específica de cada plataforma

        Ejemplo Salesys:
            self.driver.get("https://salesys.com/login")
            self.driver.find_element(By.ID, "username").send_keys(SALESYS_USER)
            ...
        """
        pass

    @abstractmethod
    def navegar_a_reporte(self):
        """
        TODO EN SUBCLASE: Navegar al reporte específico

        Ejemplo:
            self.driver.find_element(By.LINK_TEXT, "Reportes").click()
            ...
        """
        pass

    @abstractmethod
    def descargar_archivo(self) -> Path:
        """
        TODO EN SUBCLASE: Descargar el archivo de datos

        Returns:
            Path al archivo descargado
        """
        pass

    @abstractmethod
    def procesar_datos(self, ruta_archivo: Path) -> pd.DataFrame:
        """
        TODO EN SUBCLASE: Procesar el archivo descargado

        Args:
            ruta_archivo: Path al archivo descargado

        Returns:
            DataFrame procesado
        """
        pass

    def guardar_en_bd(self, df: pd.DataFrame):
        """
        TODO OPCIONAL EN SUBCLASE: Guardar datos en BD
        Sobreescribir si el scraper necesita guardar en BD.
        Por defecto no hace nada.

        Args:
            df: DataFrame a guardar
        """
        print(f"[{self.platform_name}] Guardado en BD no implementado (método opcional)")
