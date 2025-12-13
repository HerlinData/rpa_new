# ====================================
# BASE SALESYS - Login y navegación compartida
# ====================================

from scrapers.base.base_scraper import BaseScraper
from abc import ABC, abstractmethod
from pathlib import Path
from .session_manager import get_salesys_session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from config.settings import SALESYS_USER, SALESYS_PASS
import time
import shutil
from utils.file_system import renombrar_archivo


class BaseSalesys(BaseScraper):
    """
    Clase base para todos los scrapers de Salesys.
    """

    def __init__(self, reporte_nombre: str, session_manager=None):
        """
        Inicializa el scraper de Salesys.
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
        """
        if not self.session_manager.is_logged_in():
            raise Exception(f"[{self.platform_name}] Sesión no establecida")
        print(f"[{self.platform_name}] ✓ Sesión activa verificada para {self.reporte_nombre}")

    def cerrar(self):
        """
        NO cierra el driver (lo maneja SessionManager al final).
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

    def fill_dates(self, fecha_sistema):
        """Llena los campos de fecha del formulario"""
        from_id, to_id = self.get_date_field_ids()
        
        # Llenar fecha FROM
        fecha_from = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, from_id))
        )
        fecha_from.clear()
        fecha_from.send_keys(fecha_sistema)
        
        # Llenar fecha TO
        fecha_to = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, to_id))
        )
        fecha_to.clear()
        fecha_to.send_keys(fecha_sistema)
        
        # Ocultar calendario flotante
        self._hide_datepicker()
    
    def _hide_datepicker(self):
        """Oculta el calendario flotante jQuery UI"""
        for _ in range(3):
            try:
                calendar = WebDriverWait(self.driver, 1).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker"))
                )
                self.driver.execute_script("arguments[0].style.display = 'none';", calendar)
                WebDriverWait(self.driver, 1).until_not(
                    EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker"))
                )
                break
            except TimeoutException:
                break
    
    def submit_form(self):
        """Envía el formulario haciendo click en el botón submit"""
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, "subreport"))
        ).click()
        print(f"[{self.platform_name}] Formulario enviado.")
    
    def wait_for_results_tab(self):
        """Espera y cambia a la pestaña de resultados, con diagnóstico mejorado."""
        print(f"[{self.platform_name}] Esperando nueva pestaña... (Pestañas actuales: {len(self.driver.window_handles)})")
        print(f"[{self.platform_name}] URL actual antes de la espera: {self.driver.current_url}")

        t5b_start = time.time()
        timeout_new_tab = 30
        
        while time.time() - t5b_start < timeout_new_tab:
            if len(self.driver.window_handles) > 2: # Asumiendo 2 pestañas: original + formulario
                self.driver.switch_to.window(self.driver.window_handles[-1])
                print(f"[{self.platform_name}] Nueva pestaña detectada. URL: {self.driver.current_url}")
                return
            time.sleep(1)
        
        # --- INICIO DE DIAGNÓSTICO DE TIMEOUT ---
        print(f"[{self.platform_name}] [DIAGNÓSTICO] Timeout. No se abrió una nueva pestaña.")
        try:
            num_handles = len(self.driver.window_handles)
            current_url = self.driver.current_url
            print(f"[{self.platform_name}] [DIAGNÓSTICO] Pestañas al final: {num_handles}")
            print(f"[{self.platform_name}] [DIAGNÓSTICO] URL final: {current_url}")
            
            # Guardar captura de pantalla para depuración
            screenshot_path = f"debug_timeout_{self.reporte_nombre}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"[{self.platform_name}] [DIAGNÓSTICO] Captura de pantalla guardada en: {screenshot_path}")
        except Exception as diag_e:
            print(f"[{self.platform_name}] [DIAGNÓSTICO] Error adicional durante el diagnóstico: {diag_e}")
        # --- FIN DE DIAGNÓSTICO ---

        raise TimeoutException("No se abrió la pestaña de resultados en tiempo")
    
    def check_no_data_conditions(self):
        """
        Verifica condiciones de 'no data found'
        """
        # Verificar popup "No data found"
        try:
            popup = WebDriverWait(self.driver, 4).until(
                EC.presence_of_element_located((By.ID, "MGSJE"))
            )
            if "no data found" in popup.text.lower():
                print(f"[{self.platform_name}] [WARNING] No data found (en popup #MGSJE)")
                return {'status': "no_data", 'mensaje': "No data found"}
        except TimeoutException:
            pass
        
        # Verificar alertas JavaScript
        for _ in range(1): # Reduced from 10 to 1 for efficiency if multiple checks aren't strictly needed
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                print(f"[{self.platform_name}] [WARNING] Pop-up detectado y cerrado: '{alert_text}'")
                return {'status': "popup", 'mensaje': f"Pop-up cerrado: {alert_text}"}
            except NoAlertPresentException:
                break # Exit loop if no alert is present
            except Exception: # Catch other potential exceptions during alert handling
                pass
        
        return None
    
    def return_to_form(self):
        """Regresa a la pestaña del formulario"""
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[1])
        else:
            print(f"[{self.platform_name}] No queda pestaña de formulario para regresar.")

    def _process_file(self, archivo_descargado, fecha_dt, **kwargs):
        """
        Procesa el archivo descargado: renombra y mueve a su destino final.
        """
        if not archivo_descargado:
            print(f"[{self.platform_name}] [WARNING] No se detectó ninguna descarga.")
            return

        # Generar nuevo nombre para el archivo
        nuevo_nombre = self.generate_filename(fecha_dt, **kwargs)
        if not nuevo_nombre.endswith(archivo_descargado.suffix):
             nuevo_nombre += archivo_descargado.suffix

        # Renombrar el archivo en la carpeta temporal de la sesión
        new_path = self.driver.download_dir / nuevo_nombre
        if not renombrar_archivo(archivo_descargado, new_path, log_fn=print):
             print(f"[{self.platform_name}] [ERROR] No se pudo renombrar el archivo '{archivo_descargado.name}'.")
             return

        # Obtener rutas de destino
        destinos = self.get_destination_paths(nuevo_nombre, fecha_dt, **kwargs)

        # Mover archivo a los destinos
        for i, dest in enumerate(destinos):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if i == 0:
                    # Mover el primer archivo
                    shutil.move(new_path, dest)
                else:
                    # Copiar para los siguientes destinos
                    shutil.copy2(destinos[0], dest)
                print(f"[{self.platform_name}] ✓ Archivo movido a: {dest}")
            except Exception as e:
                print(f"[{self.platform_name}] [ERROR] No se pudo mover/copiar el archivo a '{dest}': {e}")


    # ====================================
    # MÉTODOS ABSTRACTOS (a implementar en subclases)
    # ====================================

    @abstractmethod
    def get_date_field_ids(self):
        """
        Retorna tupla con IDs de campos de fecha (from_id, to_id)
        Debe ser implementado por cada clase derivada
        """
        pass
    
    @abstractmethod
    def fill_additional_fields(self, **kwargs):
        """
        Llena campos específicos del formulario (dropdowns, etc.)
        Debe ser implementado por cada clase derivada
        """
        pass
    
    @abstractmethod
    def generate_filename(self, fecha_dt, **kwargs):
        """
        Genera el nombre del archivo basado en la fecha y parámetros específicos
        Debe ser implementado por cada clase derivada
        """
        pass
    
    @abstractmethod
    def get_destination_paths(self, nuevo_nombre, fecha_dt, **kwargs):
        """
        Genera las rutas de destino para el archivo
        Debe ser implementado por cada clase derivada
        """
        pass