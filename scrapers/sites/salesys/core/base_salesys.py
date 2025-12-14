from scrapers.base.base_scraper import BaseScraper
from abc import ABC, abstractmethod
from pathlib import Path
from .session_manager import get_salesys_session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from config.settings import SALESYS_USER, SALESYS_PASS, ROUTES
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

    def _run_main_flow(self, **kwargs):
        """Flujo principal: navegar a formulario e iterar sobre work items."""
        fechas = kwargs.get('fechas')
        if not fechas:
            raise ValueError("El método 'ejecutar' debe ser llamado con el argumento 'fechas'.")

        self.navegar_a_reporte()
        kwargs_clean = {k: v for k, v in kwargs.items() if k != 'fechas'}
        work_items = self._get_work_items(fechas=fechas, **kwargs_clean)

        for item in work_items:
            display_item = f"{item[0]} - {item[1]}" if isinstance(item, tuple) else str(item)
            print(f"\n[{display_item}]")
            try:
                self._descargar_para_item(item)
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue

    def _descargar_para_item(self, work_item):
        """Descarga un solo item (fecha o fecha+producto/usuario)."""
        # Desempaquetar work item
        if isinstance(work_item, tuple):
            fecha = work_item[0]
            config = ROUTES.get(self.reporte_nombre, {})
            item_kwargs = {'usuario': work_item[1]} if 'usuarios' in config else {'producto': work_item[1]}
        else:
            fecha, item_kwargs = work_item, {}

        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d") if isinstance(fecha, str) else fecha
        fecha_sistema = fecha_dt.strftime('%Y/%m/%d')

        try:
            self.fill_dates(fecha_sistema)
            self.fill_additional_fields(**item_kwargs)
            self.submit_form()

            if self.check_no_data_conditions_fast():
                print(f"  ⓘ Sin datos")
                return

            self.wait_for_results_tab()

            if self.check_no_data_conditions():
                print(f"  ⓘ Sin datos")
                self.return_to_form()
                return

            download_elem = self.driver.esperar(By.CLASS_NAME, "download", timeout=20)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_elem)
            download_elem.click()

            archivo_descargado = self.driver.esperar_descarga(extension=".csv", timeout=60)
            self._process_file(archivo_descargado, fecha_dt, **item_kwargs)
            self.return_to_form()

        except Exception as e:
            print(f"  ✗ Error en descarga: {e}")
            self.return_to_form()
    
    def configurar_driver(self):
        """Obtiene driver con sesión activa del SessionManager."""
        self.driver = self.session_manager.get_driver(log_fn=print)

    def login(self):
        if not self.session_manager.is_logged_in():
            raise Exception(f"[{self.platform_name}] Sesión no establecida")

    def navegar_a_reporte(self):
        self._open_form_tab()
        time.sleep(3)

        # Si no tiene sesión, cerrar y reabrir
        try:
            self.driver.find_element(By.ID, "slt-userName")
            print(f"[{self.platform_name}] [WARNING] Nueva pestaña sin sesión, reabriendo...")
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(2)
            self._open_form_tab()
            time.sleep(2)
        except:
            pass

        self._form_window_handle = self.driver.current_window_handle

    def _open_form_tab(self):
        """Abre nueva pestaña con el formulario."""
        self.driver.execute_script(f"window.open('{self.form_url}');")
        WebDriverWait(self.driver, 30).until(lambda d: len(d.window_handles) >= 2)
        self.driver.switch_to.window(self.driver.window_handles[-1])

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
        """
        Espera a que se abra la pestaña de resultados.
        Si aparece popup de "no data", no se abre pestaña nueva.
        """
        try:
            # Esperar a que haya 3 pestañas: original, formulario, y resultados
            WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) >= 3)
            self.driver.switch_to.window(self.driver.window_handles[-1])
        except TimeoutException:
            # No se abrió pestaña nueva, probablemente "no data"
            # Permanecer en la pestaña actual del formulario
            pass
    
    def check_no_data_conditions_fast(self):
        """Verificación rápida de "no data" después de submit (1-2s)."""
        time.sleep(0.5)
        return self._check_no_data(timeout=1.5, check_body=False)

    def check_no_data_conditions(self):
        """Verifica "no data" en página de resultados (2s)."""
        return self._check_no_data(timeout=2, check_body=True)

    def _check_no_data(self, timeout=2, check_body=False):
        """Verifica si aparece mensaje de "no data found"."""
        # 1. Alert de JavaScript
        try:
            alert = self.driver.switch_to.alert
            if "no data" in alert.text.lower() or "sin datos" in alert.text.lower():
                alert.accept()
                return True
            alert.accept()
        except NoAlertPresentException:
            pass

        # 2. Popup HTML #MGSJE
        try:
            popup = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "MGSJE"))
            )
            if "no data" in popup.text.lower() or "sin datos" in popup.text.lower():
                return True
        except TimeoutException:
            pass

        # 3. Body de la página (solo si se solicita)
        if check_body:
            try:
                if "no data" in self.driver.find_element(By.TAG_NAME, "body").text.lower():
                    return True
            except:
                pass

        return False
    
    def return_to_form(self):
        """Vuelve a la pestaña del formulario, cierra resultados si existen."""
        try:
            if len(self.driver.window_handles) > 2:
                self.driver.close()
            self.driver.switch_to.window(self._form_window_handle)
        except:
            if len(self.driver.window_handles) >= 2:
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
        """Cierra solo la pestaña del formulario, NO la sesión completa."""
        if hasattr(self, '_form_window_handle'):
            try:
                self.driver.switch_to.window(self._form_window_handle)
                self.driver.close()
                if len(self.driver.window_handles) > 0:
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as e:
                print(f"[{self.platform_name}] [WARNING] No se pudo cerrar pestaña: {e}")

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
    
    def fill_additional_fields(self, producto=None, usuario=None, **kwargs):
        """
        Implementación por defecto para llenar campos adicionales.
        """
        # Determinar qué valor seleccionar
        valor = producto or usuario
        if not valor:
            return  # Sin desplegable que llenar

        # Leer configuración del desplegable desde YAML
        desplegable_config = ROUTES.get(self.reporte_nombre, {}).get('desplegable')
        if not desplegable_config:
            return  # No hay desplegable configurado

        desplegable_id = desplegable_config.get('id')
        desplegable_tipo = desplegable_config.get('tipo', 'select')
        metodo = desplegable_config.get('metodo', 'value')

        if desplegable_tipo == 'chosen':
            # Click en el dropdown (Chosen.js)
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, desplegable_id))
            ).click()

            # Seleccionar por texto
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{valor}')]"))
            ).click()

            time.sleep(0.5)  # Breve pausa para que se registre la selección

        elif desplegable_tipo == 'select':
            # Select estándar HTML
            select_element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, desplegable_id))
            )
            select = Select(select_element)

            # Usar el método configurado
            if metodo == 'value':
                select.select_by_value(valor)
            elif metodo == 'text':
                select.select_by_visible_text(valor)
            elif metodo == 'index':
                select.select_by_index(int(valor))
    
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
