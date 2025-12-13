# ====================================
# SCRAPER: Salesys - Nómina
# ====================================
# Scraper específico para el reporte de Nómina de Salesys
# Hereda login y helpers de BaseSalesys

from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from pathlib import Path


class NominaScraper(BaseSalesys):
    """
    Scraper para el reporte de Nómina de Salesys.

    Hereda de BaseSalesys:
    - ✓ login() - Ya implementado (vía SessionManager)
    - ✓ _ir_a_modulo_reportes() - Helper compartido

    Solo implementa navegación/descarga/procesamiento específico de Nómina.

    Ventajas del SessionManager:
    - Si se ejecuta antes de RGAScraper, la sesión se reutiliza (sin login adicional)
    """

    def __init__(self, session_manager=None):
        """
        Inicializa el scraper de Nómina.

        Args:
            session_manager: SessionManager de SalesYs (opcional, se crea automáticamente)
        """
        super().__init__(reporte_nombre="Nomina", session_manager=session_manager)

    def navegar_a_reporte(self):
        """Navega específicamente al reporte de Nómina."""
        self._ir_a_modulo_reportes()

        # Navegación específica de Nómina (diferente a RGA)
        # Ejemplo:
        # self.driver.click(By.LINK_TEXT, "Recursos Humanos")
        # self.driver.click(By.LINK_TEXT, "Nómina")
        # self.driver.esperar(By.ID, "form-nomina", timeout=10)

        print(f"[{self.platform_name}] TODO: Navegar específicamente a reporte Nómina")

    def descargar_archivo(self) -> Path:
        """Descarga el archivo de reporte de Nómina."""
        # Ejemplo:
        # self.driver.click(By.ID, "btn-exportar-nomina")
        # archivo = self.driver.esperar_descarga(extension=".xlsx", timeout=60)
        # return archivo

        print(f"[{self.platform_name}] TODO: Descargar archivo Nómina")
        return self.driver.download_dir / "nomina.xlsx"
