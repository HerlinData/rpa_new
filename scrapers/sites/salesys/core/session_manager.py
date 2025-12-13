# ====================================
# SALESYS SESSION MANAGER
# ====================================
# Gestor de sesión específico para la plataforma SalesYs
# Implementa login y reutilización de sesión para todos los scrapers de SalesYs

from utils.base_session_manager import BaseSessionManager
from utils.selenium_driver import SeleniumDriver
from config.settings import (
    SALESYS_URL,
    SALESYS_USER,
    SALESYS_PASS,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_TIMEOUT
)
from selenium.webdriver.common.by import By
import time


class SalesYsSessionManager(BaseSessionManager):
    """
    Gestor de sesión para plataforma SalesYs.

    Ventajas:
    - Un solo login para todos los scrapers de SalesYs (Nómina, RGA, Ventas, etc.)
    - Reutilización automática de sesión activa
    - Reintentos automáticos de login si falla
    """

    @property
    def platform_name(self) -> str:
        """Nombre de la plataforma"""
        return "SalesYs"

    def _perform_login(self) -> bool:
        """
        Login específico de SalesYs con reintentos.
        """
        try:
            # Crear driver
            self._driver = SeleniumDriver()
            self._log(f"[{self.platform_name}] Driver creado correctamente")

            # Intentar login con reintentos
            for attempt in range(MAX_LOGIN_ATTEMPTS):
                self._log(f"[{self.platform_name}] Intento de login #{attempt + 1}/{MAX_LOGIN_ATTEMPTS}")

                try:
                    # Navegar a página de login
                    self._driver.get(SALESYS_URL)
                    self._log(f"[{self.platform_name}] Navegando a {SALESYS_URL}")

                    # Implementación de login de Salesys
                    self._driver.get(SALESYS_URL)
                    self._driver.find_element(By.ID, "extension").clear()
                    self._driver.find_element(By.ID, "extension").send_keys("4271") # Hardcoded extension from user's code
                    self._driver.find_element(By.ID, "deviceName").clear()
                    self._driver.find_element(By.ID, "deviceName").send_keys("PC4271") # Hardcoded device from user's code
                    self._driver.find_element(By.ID, "submitButton").click()
                    self._driver.find_element(By.ID, "slt-userName").clear()
                    self._driver.find_element(By.ID, "slt-userName").send_keys(SALESYS_USER)
                    self._driver.find_element(By.ID, "slt-userPass").clear()
                    self._driver.find_element(By.ID, "slt-userPass").send_keys(SALESYS_PASS)
                    self._driver.find_element(By.XPATH, "//input[@type='submit']").click()
                    time.sleep(2.2)
                    self._driver.refresh()
                    time.sleep(1.1)

                    # Si llegaste hasta aquí sin excepciones, login exitoso
                    self._logged_in = True
                    self._log(f"[{self.platform_name}] ✓ Login exitoso")
                    return True

                except Exception as e:
                    self._log(f"[{self.platform_name}] ⚠ Intento #{attempt + 1} fallido: {e}")
                    if attempt < MAX_LOGIN_ATTEMPTS - 1:
                        time.sleep(2)  # Esperar antes de reintentar
                    else:
                        self._log(f"[{self.platform_name}] ✗ Todos los intentos de login fallaron")

            return False

        except Exception as e:
            self._log(f"[{self.platform_name}] ✗ Error crítico durante login: {e}")
            return False


# ====================================
# HELPER FUNCTION
# ====================================
def get_salesys_session():
    """
    Función helper para obtener la instancia singleton del SessionManager de SalesYs.

    Returns:
        SalesYsSessionManager: Instancia singleton del gestor de sesión

    Ejemplo:
        session = get_salesys_session()
        driver = session.get_driver()
    """
    return SalesYsSessionManager()
