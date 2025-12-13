import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from config.form_routes import FORM_ROUTES
from config.settings import SALESYS_USERNAME, SALESYS_PASSWORD, MESES_ES, MAX_LOGIN_ATTEMPTS, LOGIN_URL
from core.utils import limpiar_temp, esperar_archivo, renombrar_archivo
from core.login import salesys_login

# Importar configuración centralizada de Selenium
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.selenium_config import create_silent_driver
from utils.temp_manager import get_temp_manager
from utils.salesys.session_manager import get_salesys_session

class BaseReportDownloader(ABC):
    """
    Clase base abstracta para descargadores de reportes SaleSys.
    Maneja toda la funcionalidad común: login, navegación, fechas, descarga.
    """
    
    def __init__(self, form_name, ruta_base=r"Z:\\DESCARGA INFORMES", temp_folder=None, log_fn=None):
        self.form_name = form_name
        self.form_config = FORM_ROUTES[form_name]
        self.form_url = self.form_config["form_url"]
        self.ruta_base = ruta_base
        self.log_fn = log_fn
        self.driver = None

        # Configurar gestor temporal
        self.temp_manager = get_temp_manager()
        scraper_name = f"{form_name.lower()}_scraper"
        # temp_folder se establecerá en setup_driver() desde SessionManager
        self.temp_folder = temp_folder
        self.scraper_name = scraper_name
        
    def log(self, msg):
        """Función de logging unificada"""
        if self.log_fn:
            self.log_fn(msg)
        else:
            print(msg)
    
    def setup_driver(self):
        """Obtiene driver desde SessionManager (sesión compartida)"""
        # Obtener driver desde SessionManager (login compartido)
        session = get_salesys_session()
        is_first_scraper = not session.is_logged_in()  # Detectar si es el primero

        self.driver = session.get_driver(temp_folder=self.temp_folder, log_fn=self.log_fn)

        # IMPORTANTE: Usar la carpeta temporal del SessionManager (compartida)
        # porque Chrome no permite cambiar directorio de descargas después de iniciado
        self.temp_folder = session.get_temp_folder()

        # Solo limpiar en el primer scraper (evitar borrar descargas de scrapers previos)
        if is_first_scraper:
            limpiar_temp(self.temp_folder)
            self.log(f"[SESSION] Carpeta temporal limpiada (primer scraper)")

        self.log(f"[SESSION] Driver obtenido desde sesión compartida")
        self.log(f"[SESSION] Usando carpeta temporal compartida: {self.temp_folder}")
        return True
    
    def perform_login_and_navigate(self):
        """
        Navega al formulario (login ya realizado por SessionManager)
        """
        try:
            # El driver ya tiene sesión activa gracias a SessionManager
            # Solo necesitamos abrir el formulario en nueva pestaña

            self.log(f"[NAVIGATE] Abriendo formulario: {self.form_url}")

            # Abrir formulario en nueva pestaña
            self.driver.execute_script(f"window.open('{self.form_url}');")
            WebDriverWait(self.driver, 30).until(lambda d: len(d.window_handles) > 1)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(self.form_url)
            time.sleep(3)

            # Verificar llegada al formulario
            WebDriverWait(self.driver, 8).until(lambda d: d.current_url.startswith("http"))
            if self.driver.current_url.lower().startswith(self.form_url.lower()):
                self.log("[SUCCESS] Navegación al formulario exitosa")
                return True
            else:
                raise Exception(f"No se llegó al formulario esperado. URL actual: {self.driver.current_url}")

        except Exception as e:
            self.log(f"[ERROR] Error navegando al formulario: {e}")
            raise
        
        return True
    
    @abstractmethod
    def get_date_field_ids(self):
        """
        Retorna tupla con IDs de campos de fecha (from_id, to_id)
        Debe ser implementado por cada clase derivada
        """
        pass
    
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
    
    @abstractmethod
    def fill_additional_fields(self, **kwargs):
        """
        Llena campos específicos del formulario (dropdowns, etc.)
        Debe ser implementado por cada clase derivada
        """
        pass
    
    def submit_form(self):
        """Envía el formulario haciendo click en el botón submit"""
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, "subreport"))
        ).click()
        self.log("Formulario enviado.")
    
    def wait_for_results_tab(self):
        """Espera y cambia a la pestaña de resultados"""
        t5b_start = time.time()
        timeout_new_tab = 30
        
        while len(self.driver.window_handles) <= 2 and time.time() - t5b_start < timeout_new_tab:
            WebDriverWait(self.driver, 2).until(lambda d: True)
        
        if len(self.driver.window_handles) > 2:
            self.driver.switch_to.window(self.driver.window_handles[-1])
        else:
            raise TimeoutException("No se abrió la pestaña de resultados en tiempo")
    
    def check_no_data_conditions(self):
        """
        Verifica condiciones de 'no data found'
        Retorna diccionario con status y mensaje si se detecta sin datos
        """
        # Verificar popup "No data found"
        try:
            popup = WebDriverWait(self.driver, 4).until(
                EC.presence_of_element_located((By.ID, "MGSJE"))
            )
            if "no data found" in popup.text.lower():
                self.log("[WARNING] No data found (en popup #MGSJE)")
                return {'status': "no_data", 'mensaje': "No data found"}
        except TimeoutException:
            pass
        
        # Verificar alertas JavaScript
        for _ in range(10):
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                self.log(f"[WARNING] Pop-up detectado y cerrado: '{alert_text}'")
                return {'status': "popup", 'mensaje': f"Pop-up cerrado: {alert_text}"}
            except Exception:
                time.sleep(0.2)
        
        return None
    
    def download_file(self):
        """Ejecuta la descarga del archivo"""
        try:
            elem_descarga = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "download"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem_descarga)
            elem_descarga.click()
            self.log("Clic en botón de descarga enviado.")
            
            # Esperar archivo descargado
            descarga_start = time.time()
            archivo_descargado = esperar_archivo(self.temp_folder, descarga_start, ext=".csv", timeout=30)
            
            return archivo_descargado
            
        except TimeoutException:
            self.log("No apareció el botón de descarga")
            return None
    
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
    
    def process_downloaded_file(self, archivo_descargado, fecha_dt, **kwargs):
        """Procesa el archivo descargado: renombra y mueve a destinos"""
        if not archivo_descargado:
            return {'status': 'no_descarga', 'mensaje': 'Descarga NO detectada en tiempo'}
        
        # Generar nuevo nombre
        ext = os.path.splitext(archivo_descargado)[1]
        nuevo_nombre = self.generate_filename(fecha_dt, **kwargs) + ext
        
        # Renombrar archivo
        old_path = os.path.join(self.temp_folder, archivo_descargado)
        new_path = os.path.join(self.temp_folder, nuevo_nombre)
        
        if not renombrar_archivo(old_path, new_path):
            return {'status': 'error', 'mensaje': f"No se pudo renombrar '{archivo_descargado}'"}
        
        # Obtener rutas de destino
        destinos = self.get_destination_paths(nuevo_nombre, fecha_dt, **kwargs)
        
        # Mover archivo a destinos
        moved_paths = []
        for dest in destinos:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if os.path.exists(new_path):
                os.replace(new_path, dest)
                moved_paths.append(str(dest))
                self.log(f"Archivo movido a: {dest}")
            else:
                # Si ya se movió, crear copia
                import shutil
                shutil.copy2(destinos[0], dest)
                moved_paths.append(str(dest))
        
        return {'status': 'descargado', 'mensaje': f'Movido a: {moved_paths}'}
    
    def return_to_form(self):
        """Regresa a la pestaña del formulario"""
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[1])
        else:
            self.log("No queda pestaña de formulario.")
    
    def process_single_download(self, fecha, **kwargs):
        """
        Procesa una descarga individual con todos los pasos
        Retorna diccionario con resultado
        """
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d") if isinstance(fecha, str) else fecha
        fecha_sistema = fecha_dt.strftime('%Y/%m/%d')

        res = {'status': None, 'mensaje': ''}

        # Remover 'fecha' de kwargs si existe para evitar duplicados
        kwargs_clean = {k: v for k, v in kwargs.items() if k not in ('fecha', 'fechas')}

        try:
            # Asegurar que estamos en la pestaña del formulario
            self.driver.switch_to.window(self.driver.window_handles[1])

            # 1. Llenar fechas
            self.fill_dates(fecha_sistema)

            # 2. Llenar campos adicionales específicos
            self.fill_additional_fields(**kwargs_clean)

            # 3. Enviar formulario
            self.submit_form()

            # 4. Esperar pestaña de resultados
            self.wait_for_results_tab()

            # 5. Verificar condiciones de "no data"
            no_data_result = self.check_no_data_conditions()
            if no_data_result:
                res = no_data_result
            else:
                # 6. Descargar archivo
                archivo_descargado = self.download_file()

                # 7. Procesar archivo descargado
                res = self.process_downloaded_file(archivo_descargado, fecha_dt, **kwargs_clean)

            # 8. Regresar al formulario
            self.return_to_form()

        except Exception as e:
            res = {'status': 'error', 'mensaje': f'Excepción general: {e}'}
            self.log(f"[ERROR] {e}")
            self.return_to_form()

        return res
    
    def download_reports(self, fechas, **kwargs):
        """
        Método principal para descargar reportes
        Puede ser sobrescrito para lógica específica
        """
        if not self.setup_driver():
            raise Exception("No se pudo configurar el driver")

        # Limpiar kwargs de parámetros que no deben pasarse a process_single_download
        kwargs_clean = {k: v for k, v in kwargs.items() if k not in ('fecha', 'fechas', 'log_fn')}

        try:
            # Login y navegación inicial
            self.perform_login_and_navigate()

            # Procesar cada fecha
            for fecha in fechas:
                self.log(f"\n[SCHEDULE] ==== Fecha: {fecha} ====")
                result = self.process_single_download(fecha, **kwargs_clean)

                status_msg = f"[{result['status'].upper()}] {result['mensaje']}"
                self.log(status_msg)

            return True

        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Limpieza final de recursos
        NOTA: NO cierra el driver ni la carpeta temporal porque son compartidos
        Solo cierra pestañas adicionales que haya abierto este scraper
        """
        try:
            if self.driver:
                # Cerrar solo las pestañas adicionales (mantener la primera)
                while len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()

                # Volver a la pestaña principal
                if len(self.driver.window_handles) > 0:
                    self.driver.switch_to.window(self.driver.window_handles[0])

                self.driver = None  # Liberar referencia local
                self.log("[INFO] Pestañas cerradas (driver y carpeta temporal compartidos mantenidos)")
        except Exception as e:
            self.log(f"[WARNING] Error cerrando pestañas: {e}")

        # NO limpiar carpeta temporal aquí - es compartida por todos los scrapers
        # La limpieza se hace al final por el SessionManager