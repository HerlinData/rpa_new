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
from datetime import datetime

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

    # =================================================
    # --- IMPLEMENTACIÓN DEL FLUJO PRINCIPAL (TEMPLATE) ---
    # =================================================

    def _run_main_flow(self, **kwargs):
        """
        Implementa el flujo de trabajo principal para los scrapers de Salesys.
        Este método es llamado por el `ejecutar` de la clase base.
        """
        fechas = kwargs.get('fechas')
        if not fechas:
            raise ValueError("El método 'ejecutar' debe ser llamado con el argumento 'fechas'.")

        # Navegar a la página del reporte una sola vez
        self.navegar_a_reporte()

        # Limpiar kwargs para evitar duplicados (fechas ya se pasa explícitamente)
        kwargs_clean = {k: v for k, v in kwargs.items() if k != 'fechas'}

        # Obtener la lista de "unidades de trabajo" (cada scraper la define)
        work_items = self._get_work_items(fechas=fechas, **kwargs_clean)

        # Iterar sobre cada unidad de trabajo para descargar el reporte
        for item in work_items:
            # Formatear el item para display más limpio
            if isinstance(item, tuple):
                # RGA: (fecha, producto)
                display_item = f"{item[0]} - {item[1]}"
            else:
                # Estado Agente: solo fecha
                display_item = str(item)

            print(f"\n[{display_item}]")
            try:
                self._descargar_para_item(item)
            except Exception as e:
                print(f"  ✗ Error: {e}")
                # Opcional: decidir si continuar con la siguiente unidad o detener todo
                continue 

    # =================================================
    # --- ORQUESTACIÓN DE DESCARGA PARA UN SOLO ITEM ---
    # =================================================

    def _descargar_para_item(self, work_item):
        """
        Orquesta la secuencia completa de descarga para una única unidad de trabajo.
        """
        # 1. Desempaquetar la unidad de trabajo
        # Para scrapers simples, es solo la fecha. Para RGA, es (fecha, producto).
        if isinstance(work_item, tuple):
            fecha = work_item[0]
            # Convertir el resto de la tupla en un diccionario de kwargs
            item_kwargs = {'producto': work_item[1]} # Asume que el segundo item es 'producto'
        else:
            fecha = work_item
            item_kwargs = {}
            
        # 2. Preparar fechas para el formulario
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d") if isinstance(fecha, str) else fecha
        fecha_sistema = fecha_dt.strftime('%Y/%m/%d')
        
        try:
            # 3. Llenar el formulario con los datos del item
            self.fill_dates(fecha_sistema)
            self.fill_additional_fields(**item_kwargs)

            # 4. Enviar formulario
            self.submit_form()

            # 5. Esperar pestaña de resultados
            self.wait_for_results_tab()

            # 6. Verificar si no hay datos
            no_data = self.check_no_data_conditions()
            if no_data:
                print(f"  ⓘ Sin datos")
                self.return_to_form()
                return

            # 7. Descargar el archivo
            download_button_selector = (By.CLASS_NAME, "download") # Asunción genérica
            download_elem = self.driver.esperar(*download_button_selector, timeout=20)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_elem)
            download_elem.click()
            
            # Asumimos .csv basado en implementaciones anteriores
            archivo_descargado = self.driver.esperar_descarga(extension=".csv", timeout=60)
            
            # 8. Procesar el archivo (renombrar y mover)
            self._process_file(archivo_descargado, fecha_dt, **item_kwargs)
            
            # 9. Volver al formulario para el siguiente item
            self.return_to_form()

        except Exception as e:
            print(f"  ✗ Error en descarga: {e}")
            self.return_to_form() # Intentar volver al formulario para no romper el bucle
            # No relanzamos el error para permitir que el bucle principal continúe
            # raise

    # =================================================
    # --- MÉTODOS DE AYUDA (LÓGICA COMÚN) ---
    # =================================================
    
    def configurar_driver(self):
        """
        Obtiene driver con sesión activa del SessionManager.
        """
        self.driver = self.session_manager.get_driver(log_fn=print)

    def login(self):
        if not self.session_manager.is_logged_in():
            raise Exception(f"[{self.platform_name}] Sesión no establecida")

    def navegar_a_reporte(self):
        self.driver.execute_script(f"window.open('{self.form_url}');")
        # Esperar a que haya 2 pestañas: la original y la del formulario
        WebDriverWait(self.driver, 30).until(lambda d: len(d.window_handles) >= 2)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Guardar referencia a la pestaña del formulario actual
        self._form_window_handle = self.driver.current_window_handle

        time.sleep(2)

    def fill_dates(self, fecha_sistema):
        from_id, to_id = self.get_date_field_ids()
        fecha_from = self.driver.esperar(By.ID, from_id, timeout=30)
        fecha_from.clear()
        fecha_from.send_keys(fecha_sistema)
        fecha_to = self.driver.esperar(By.ID, to_id, timeout=30)
        fecha_to.clear()
        fecha_to.send_keys(fecha_sistema)
        self._hide_datepicker()
    
    def _hide_datepicker(self):
        try:
            calendar = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker")))
            self.driver.execute_script("arguments[0].style.display = 'none';", calendar)
        except TimeoutException:
            pass
    
    def submit_form(self):
        self.driver.click(By.ID, "subreport", timeout=30)

    def wait_for_results_tab(self):
        # Esperar a que haya 3 pestañas: original, formulario, y resultados
        WebDriverWait(self.driver, 30).until(lambda d: len(d.window_handles) >= 3)
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def check_no_data_conditions(self):
        try:
            popup = WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.ID, "MGSJE")))
            if "no data found" in popup.text.lower():
                return {'status': "no_data", 'mensaje': "No data found"}
        except TimeoutException:
            pass
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return {'status': "popup", 'mensaje': f"Pop-up cerrado: {alert_text}"}
        except NoAlertPresentException:
            pass
        return None
    
    def return_to_form(self):
        # La pestaña de resultados se cierra, volvemos a la del formulario
        if len(self.driver.window_handles) > 2:
             self.driver.close() # Cierra la pestaña actual (resultados)

        # Volver a la pestaña del formulario específica de este scraper
        if hasattr(self, '_form_window_handle'):
            self.driver.switch_to.window(self._form_window_handle)
        else:
            # Fallback a comportamiento anterior si no hay referencia guardada
            self.driver.switch_to.window(self.driver.window_handles[1])

    def _process_file(self, archivo_descargado, fecha_dt, **kwargs):
        if not archivo_descargado:
            print(f"[WARNING] No se detectó ninguna descarga.")
            return
        nuevo_nombre = self.generate_filename(fecha_dt, **kwargs)
        if not nuevo_nombre.endswith(archivo_descargado.suffix):
             nuevo_nombre += archivo_descargado.suffix
        new_path = self.driver.download_dir / nuevo_nombre
        if not renombrar_archivo(archivo_descargado, new_path, log_fn=print):
             print(f"[ERROR] No se pudo renombrar el archivo '{archivo_descargado.name}'.")
             return
        destinos = self.get_destination_paths(nuevo_nombre, fecha_dt, **kwargs)
        for i, dest in enumerate(destinos):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if i == 0:
                    shutil.move(new_path, dest)
                else:
                    shutil.copy2(destinos[0], dest)
                # Mostrar solo el nombre del archivo, no la ruta completa
                print(f"  ✓ {nuevo_nombre}")
            except Exception as e:
                print(f"  ✗ Error moviendo archivo: {e}")
    
    def cerrar(self):
        """
        Cierra la pestaña del formulario de este scraper.
        El driver permanece activo para otros scrapers.
        """
        # Cerrar la pestaña del formulario de este scraper
        if hasattr(self, '_form_window_handle'):
            try:
                # Cambiar a la pestaña del formulario y cerrarla
                self.driver.switch_to.window(self._form_window_handle)
                self.driver.close()

                # Volver a la pestaña principal (login)
                if len(self.driver.window_handles) > 0:
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as e:
                print(f"[{self.platform_name}] [WARNING] No se pudo cerrar la pestaña: {e}")

    # =======================================================================
    # -- MÉTODOSABSTRACTOS (a ser implementados por los scrapers hijos) --
    # =======================================================================

    @abstractmethod
    def _get_work_items(self, fechas, **kwargs) -> list:
        """
        Debe generar la lista de 'unidades de trabajo' a procesar.
        """
        pass

    @property
    @abstractmethod
    def form_url(self) -> str:
        """
        Debe devolver la URL del formulario específico del reporte.
        """
        pass

    @abstractmethod
    def get_date_field_ids(self) -> tuple:
        """
        Debe devolver una tupla con los IDs de los campos de fecha. Ej: ("from", "to")
        """
        pass
    
    @abstractmethod
    def fill_additional_fields(self, **kwargs):
        """
        Debe implementar el llenado de campos adicionales específicos del formulario.
        """
        pass
    
    @abstractmethod
    def generate_filename(self, fecha_dt, **kwargs) -> str:
        """
        Debe generar el nombre base del archivo final.
        """
        pass
    
    @abstractmethod
    def get_destination_paths(self, nuevo_nombre, fecha_dt, **kwargs) -> list:
        """
        Debe generar la lista de rutas de destino finales para el archivo.
        """
        pass
