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
    def ejecutar(self, fechas: list, **kwargs):
        """
        Ejecuta el flujo completo del scraper para una lista de fechas.
        """
        try:
            print(f"[{self.platform_name}] Iniciando scraper...")

            # 1. Configurar driver y hacer login una sola vez
            self.configurar_driver()
            self.login()

            # 2. Navegar a la página del reporte una sola vez
            self.navegar_a_reporte()

            # 3. Iterar sobre cada fecha para descargar el reporte
            for fecha in fechas:
                print(f"\n--- Procesando fecha: {fecha} ---")
                try:
                    self.descargar_archivo(fecha=fecha, **kwargs)
                except Exception as e:
                    print(f"[{self.platform_name}] ✗ Error procesando fecha {fecha}: {e}")
                    # Opcional: decidir si continuar con la siguiente fecha o detener todo
                    # continue 

            print(f"\n[{self.platform_name}] ✓ Proceso completado para todas las fechas.")

        except Exception as e:
            print(f"[{self.platform_name}] ✗ Error crítico durante la ejecución: {e}")
            raise

        finally:
            # 4. Siempre cerrar al final
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
    def descargar_archivo(self, fecha, **kwargs) -> Path:
        """
        TODO_EN SUBCLASE: Descargar el archivo de datos para una fecha específica.
        """
        pass