# ====================================
# SALESYS SESSION MANAGER
# ====================================

from utils.base_session_manager import BaseSessionManager
from utils.selenium_driver import SeleniumDriver
from config.settings import (SALESYS_URL, SALESYS_USER, SALESYS_PASS, SALESYS_EXTENSION, SALESYS_DEVICE, MAX_LOGIN_ATTEMPTS, LOGIN_TIMEOUT)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SalesYsSessionManager(BaseSessionManager):
    """
    Gestor de sesión para plataforma SalesYs.
    """

    @property
    def platform_name(self) -> str:
        """Nombre de la plataforma"""
        return "SalesYs"

    def _perform_login(self) -> bool:
        """
        Login específico de SalesYs con reintentos y verificación.
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
                    
                    # Implementación de login de Salesys
                    self._driver.find_element(By.ID, "extension").clear()
                    self._driver.find_element(By.ID, "extension").send_keys(SALESYS_EXTENSION)
                    self._driver.find_element(By.ID, "deviceName").clear()
                    self._driver.find_element(By.ID, "deviceName").send_keys(SALESYS_DEVICE)
                    self._driver.find_element(By.ID, "submitButton").click()
                    
                    # Esperar a que aparezca el formulario de usuario/pass
                    WebDriverWait(self._driver, LOGIN_TIMEOUT).until(
                        EC.visibility_of_element_located((By.ID, "slt-userName"))
                    )

                    self._driver.find_element(By.ID, "slt-userName").clear()
                    self._driver.find_element(By.ID, "slt-userName").send_keys(SALESYS_USER)
                    self._driver.find_element(By.ID, "slt-userPass").clear()
                    self._driver.find_element(By.ID, "slt-userPass").send_keys(SALESYS_PASS)
                    self._driver.find_element(By.XPATH, "//input[@type='submit']").click()
                    
                    # --- VERIFICACIÓN DE LOGIN ---
                    # Esperar un momento para que la página reaccione
                    time.sleep(3)

                    # Verificar si el login fue exitoso. Si el campo de usuario aún existe, falló.
                    try:
                        self._driver.find_element(By.ID, "slt-userName")
                        # Si encuentra el elemento, el login falló. Forzamos un error para reintentar.
                        raise Exception("Credenciales inválidas o la página de login no cambió.")
                    except:
                        # Si NO encuentra el elemento, el login fue exitoso.
                        self._logged_in = True
                        self._log(f"[{self.platform_name}] ✓ Login verificado y exitoso")

                        # Esperar adicional para que las cookies/sesión se establezcan completamente
                        time.sleep(2)
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
    """
    return SalesYsSessionManager()
