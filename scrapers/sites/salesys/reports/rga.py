# ====================================
# SCRAPER: Salesys - RGA
# ====================================
# Scraper específico para el reporte RGA de Salesys
# Hereda login y helpers de BaseSalesys

from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from pathlib import Path
import time


class RGAScraper(BaseSalesys):
    """
    Scraper para el reporte RGA de Salesys.

    Hereda de BaseSalesys:
    - ✓ login() - Ya implementado (vía SessionManager)
    - ✓ _ir_a_modulo_reportes() - Helper compartido

    Solo implementa:
    - navegar_a_reporte() - Navegación específica a RGA
    - descargar_archivo() - Descarga específica de RGA

    Ventajas del SessionManager:
    - Si se ejecuta después de NominaScraper, reutiliza la misma sesión (sin login)
    """

    def __init__(self, session_manager=None):
        """
        Inicializa el scraper de RGA.

        Args:
            session_manager: SessionManager de SalesYs (opcional, se crea automáticamente)
        """
        super().__init__(reporte_nombre="RGA", session_manager=session_manager)

    # ====================================
    # IMPLEMENTACIÓN ESPECÍFICA DE RGA
    # ====================================

    def navegar_a_reporte(self):
        """
        Navega específicamente al reporte RGA.

        TODO: Implementar navegación específica
        Pasos:
        1. Ir a módulo de reportes (usar helper)
        2. Seleccionar categoría de RGA
        3. Click en reporte RGA
        4. Esperar formulario
        """
        # Usar helper compartido
        self._ir_a_modulo_reportes()

        # Navegación específica de RGA
        # Ejemplo:
        # self.driver.click(By.LINK_TEXT, "Gestión")
        # self.driver.click(By.LINK_TEXT, "RGA")
        # self.driver.esperar(By.ID, "form-rga", timeout=10)

        print(f"[{self.platform_name}] TODO: Navegar específicamente a reporte RGA")

    def descargar_archivo(self) -> Path:
        """
        Descarga el archivo de reporte RGA.

        TODO: Implementar descarga específica
        Pasos:
        1. Seleccionar fechas/filtros (si aplica)
        2. Click en botón descargar
        3. Esperar descarga
        4. Retornar Path del archivo descargado
        """
        # Ejemplo:
        # self.driver.click(By.ID, "btn-descargar-rga")
        # archivo = self.driver.esperar_descarga(extension=".xlsx", timeout=60)
        # return archivo

        print(f"[{self.platform_name}] TODO: Descargar archivo RGA")
        return self.driver.download_dir / "rga.xlsx"


# ====================================
# EJEMPLO DE USO
# ====================================
if __name__ == "__main__":
    from scrapers.sites.salesys.core.session_manager import get_salesys_session

    # Opción 1: Usar SessionManager explícitamente (recomendado para múltiples scrapers)
    session = get_salesys_session()
    try:
        scraper = RGAScraper(session_manager=session)
        archivo_descargado = scraper.ejecutar()
        print(f"Archivo descargado en: {archivo_descargado}")
    finally:
        session.cleanup()  # Cerrar sesión al finalizar

    # Opción 2: Uso simple (crea SessionManager automáticamente)
    # scraper = RGAScraper()
    # archivo_descargado = scraper.ejecutar()
    # print(f"Archivo descargado en: {archivo_descargado}")
