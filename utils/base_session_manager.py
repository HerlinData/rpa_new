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
    _temp_folder = None

    def __new__(cls):
        """
        Implementación del patrón Singleton.
        Garantiza una sola instancia por clase.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_driver(self, temp_folder=None, log_fn=None):
        """
        Obtiene driver con sesión activa.

        Si ya existe una sesión activa, reutiliza el driver.
        Si no, crea uno nuevo y realiza el login.

        Args:
            temp_folder: Carpeta temporal para descargas (solo primera vez)
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

        # Setup temp folder
        temp_folder_rel = temp_folder or f"./temp_scraping/{self.platform_name.lower()}_session"
        self._temp_folder = os.path.abspath(temp_folder_rel)
        os.makedirs(self._temp_folder, exist_ok=True)

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

    def get_temp_folder(self) -> str:
        """
        Obtiene la ruta de la carpeta temporal compartida.

        Returns:
            str: Ruta absoluta de la carpeta temporal
        """
        return self._temp_folder

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
                self._driver.quit()
                self._log(f"[{self.platform_name}] ✓ Sesión cerrada correctamente")
            except Exception as e:
                self._log(f"[{self.platform_name}] ⚠ Error cerrando sesión: {e}")
            finally:
                self._driver = None
                self._logged_in = False

        # Limpiar carpeta temporal compartida
        if self._temp_folder:
            try:
                temp_path = Path(self._temp_folder)
                if temp_path.exists():
                    shutil.rmtree(temp_path)
                    self._log(f"[{self.platform_name}] Carpeta temporal eliminada: {self._temp_folder}")
            except Exception as e:
                # Silenciar errores durante shutdown de Python
                if sys.meta_path is not None:
                    self._log(f"[{self.platform_name}] ⚠ Error limpiando carpeta temporal: {e}")

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
