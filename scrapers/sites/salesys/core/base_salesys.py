# ====================================
# BASE SALESYS - Login y navegación compartida
# ====================================

from scrapers.base.base_scraper import BaseScraper
from .session_manager import get_salesys_session
from selenium.webdriver.common.by import By
from config.settings import SALESYS_USER, SALESYS_PASS
import time


class BaseSalesys(BaseScraper):
    """
    Clase base para todos los scrapers de Salesys.

    Implementa:
    - Login común de Salesys (vía SessionManager)
    - Navegación a módulo de reportes
    - Helpers compartidos

    Ventajas del SessionManager:
    - Un solo login para todos los scrapers de Salesys
    - Reutilización automática de sesión
    """

    def __init__(self, reporte_nombre: str, session_manager=None):
        """
        Inicializa el scraper de Salesys.

        Args:
            reporte_nombre: Nombre del reporte (ej: "Nomina", "RGA")
            session_manager: SessionManager de SalesYs (opcional, se crea automáticamente)
        """
        super().__init__(platform_name="Salesys")
        self.reporte_nombre = reporte_nombre
        self.session_manager = session_manager or get_salesys_session()

    # ====================================
    # IMPLEMENTACIÓN COMÚN (para TODOS los scrapers de Salesys)
    # ====================================

    def configurar_driver(self):
        """
        Obtiene driver con sesión activa del SessionManager.
        Ya no crea un driver nuevo, reutiliza el del SessionManager.
        """
        self.driver = self.session_manager.get_driver(
            log_fn=print
        )
        print(f"[{self.platform_name}] ✓ Driver configurado con sesión activa")

    def login(self):
        """
        Login ya manejado por SessionManager.
        Solo verifica que la sesión esté activa.
        """
        if not self.session_manager.is_logged_in():
            raise Exception(f"[{self.platform_name}] Sesión no establecida")
        print(f"[{self.platform_name}] ✓ Sesión activa verificada para {self.reporte_nombre}")

    def cerrar(self):
        """
        NO cierra el driver (lo maneja SessionManager al final).
        El driver se reutiliza para otros scrapers de Salesys.
        """
        print(f"[{self.platform_name}] ℹ Driver permanece activo para otros scrapers")
        # NOTA: El cleanup del driver se hace en el SessionManager con session.cleanup()

    def _ir_a_modulo_reportes(self):
        """
        Helper: Navega al módulo de reportes de Salesys.
        """
        # Ejemplo:
        # self.driver.click(By.LINK_TEXT, "Reportes")
        # self.driver.esperar(By.ID, "modulo-reportes", timeout=10)

        print(f"[{self.platform_name}] TODO: Navegar a módulo de reportes")

    # ====================================
    # MÉTODOS ABSTRACTOS (implementar en subclases)
    # ====================================
    # navegar_a_reporte() - Cada reporte navega diferente
    # descargar_archivo() - Cada reporte descarga diferente
