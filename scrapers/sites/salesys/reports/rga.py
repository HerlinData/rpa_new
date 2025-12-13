# ====================================
# SCRAPER: Salesys - RGA
# ====================================
# Scraper específico para el reporte RGA de Salesys
# Hereda login y helpers de BaseSalesys

from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from pathlib import Path
import time
from config.settings import SALESYS_RGA_FORM_URL


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
        """Navega específicamente al reporte RGA."""
        print(f"[{self.platform_name}] Navegando a {SALESYS_RGA_FORM_URL}")
        self.driver.get(SALESYS_RGA_FORM_URL)
        # TODO: Añadir esperas (WebDriverWait) si la página tarda en cargar o necesita interacción inicial.

    def descargar_archivo(self) -> Path:
        """Descarga el archivo del reporte RGA."""
        # TODO: Implementar la lógica específica para descargar el archivo del reporte.
        # Esto usualmente implica:
        # 1. Seleccionar filtros/fechas (si aplica).
        # 2. Hacer clic en el botón de exportar/descargar.
        # 3. Esperar a que la descarga se complete usando self.driver.esperar_descarga().

        print(f"[{self.platform_name}] TODO: Implementar descarga para {self.reporte_nombre}")
        # Placeholder: Retorna una ruta de archivo genérica para que el flujo no se rompa.
        return self.driver.download_dir / f"{self.reporte_nombre.lower()}.xlsx"


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
