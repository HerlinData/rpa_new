# ====================================
# BASE SESSION MANAGER
# ====================================
# Gestor de sesión base genérico para cualquier plataforma web
# Implementa el patrón Singleton para reutilizar sesiones

from abc import ABC, abstractmethod
from pathlib import Path
import sys
import shutil
import os


class BaseSessionManager(ABC):
    """
    Gestor de sesión base para cualquier plataforma web.

    Patrón Singleton: Una instancia por plataforma

    Ventajas:
    - Un solo login para múltiples scrapers de la misma plataforma
    - Reutilización de sesión activa
    - Gestión centralizada del driver
    - Cleanup automático de recursos

    Uso:
        session = PlataformaSessionManager()
        driver = session.get_driver()
        # ... usar driver con sesión activa
        session.cleanup()  # Al final de todos los scrapers
    """

    _instance = None
    _driver = None
    _logged_in = False

    def __new__(cls):
        """
        Implementación del patrón Singleton.
        Garantiza una sola instancia por clase.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_driver(self, log_fn=None):
        """
        Obtiene driver con sesión activa.

        Si ya existe una sesión activa, reutiliza el driver.
        Si no, crea uno nuevo y realiza el login.

        Args:
            log_fn: Función de logging personalizada (default: print)

        Returns:
            SeleniumDriver con sesión activa

        Raises:
            Exception: Si no se puede establecer la sesión
        """
        self.log_fn = log_fn or print

        # Si ya está logueado, retornar driver existente
        if self._logged_in and self._driver:
            self._log(f"[{self.platform_name}] Reutilizando sesión activa")
            return self._driver

        # Primera vez: crear driver y hacer login
        self._log(f"[{self.platform_name}] Iniciando nueva sesión...")

        # Realizar login
        if not self._perform_login():
            raise Exception(f"No se pudo establecer sesión de {self.platform_name}")

        return self._driver

    @abstractmethod
    def _perform_login(self) -> bool:
        """
        TODO en subclase: Implementar login específico de cada plataforma.

        Este método debe:
        1. Crear self._driver usando SeleniumDriver
        2. Hacer login en la plataforma
        3. Establecer self._logged_in = True si exitoso

        Returns:
            bool: True si login exitoso, False en caso contrario
        """
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        TODO en subclase: Nombre de la plataforma.

        Ejemplos: "SalesYs", "SAP", "Oracle"

        Returns:
            str: Nombre de la plataforma
        """
        pass

    def is_logged_in(self) -> bool:
        """
        Verifica si hay una sesión activa.

        Returns:
            bool: True si hay sesión activa
        """
        return self._logged_in and self._driver is not None

    def cleanup(self):
        """
        Cierra la sesión y limpia recursos.

        Debe llamarse al final de todos los scrapers de esta plataforma.
        """
        if self._driver:
            try:
                self._log(f"[{self.platform_name}] Cerrando sesión...")

                # Intentar cerrar con timeout para evitar quedar pegado
                import threading

                def quit_driver():
                    try:
                        self._driver.quit()
                    except:
                        pass

                # Ejecutar quit en thread separado con timeout
                quit_thread = threading.Thread(target=quit_driver, daemon=True)
                quit_thread.start()
                quit_thread.join(timeout=5)  # Esperar máximo 5 segundos

                if quit_thread.is_alive():
                    self._log(f"[{self.platform_name}] ⚠ Timeout cerrando navegador (5s), forzando cierre...")
                    # Matar procesos Chrome zombies
                    self._kill_chrome_processes()
                else:
                    self._log(f"[{self.platform_name}] ✓ Sesión cerrada correctamente")

            except Exception as e:
                self._log(f"[{self.platform_name}] ⚠ Error cerrando sesión: {e}")
            finally:
                self._driver = None
                self._logged_in = False

    def _kill_chrome_processes(self):
        """
        Mata procesos Chrome/ChromeDriver zombies.
        Útil cuando el navegador crashea y no responde al quit().
        """
        try:
            import subprocess
            import platform

            if platform.system() == 'Windows':
                # Windows: taskkill
                subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'],
                             capture_output=True, timeout=3)
                subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'],
                             capture_output=True, timeout=3)
            else:
                # Linux/Mac: pkill
                subprocess.run(['pkill', '-9', 'chrome'],
                             capture_output=True, timeout=3)
                subprocess.run(['pkill', '-9', 'chromedriver'],
                             capture_output=True, timeout=3)
        except Exception:
            pass  # Ignorar errores al matar procesos

    def _log(self, msg):
        """
        Función de logging interna.

        Args:
            msg: Mensaje a loguear
        """
        if hasattr(self, 'log_fn') and self.log_fn:
            self.log_fn(msg)
        else:
            print(msg)

    def __del__(self):
        """
        Destructor: asegurar cleanup al destruir objeto.
        """
        self.cleanup()
