# ====================================
# SCRAPER: Salesys - Estado Agente
# ====================================
# Scraper específico para el reporte de Estado Agente de Salesys
# Hereda login y helpers de BaseSalesys

from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from pathlib import Path
from config.settings import SALESYS_ESTADO_AGENTE_V2_FORM_URL


class EstadoAgenteV2Scraper(BaseSalesys):
    """
    Scraper para el reporte de Estado Agente de Salesys.
    """

    def __init__(self, session_manager=None):
        """
        Inicializa el scraper de Estado Agente.
        """
        super().__init__(reporte_nombre="EstadoAgenteV2", session_manager=session_manager)

    def navegar_a_reporte(self):
        """Navega específicamente al reporte de Estado Agente V2."""
        print(f"[{self.platform_name}] Navegando a {SALESYS_ESTADO_AGENTE_V2_FORM_URL}")

        # Abrir formulario en nueva pestaña (como el código original)
        import time
        from selenium.webdriver.support.ui import WebDriverWait

        self.driver.execute_script(f"window.open('{SALESYS_ESTADO_AGENTE_V2_FORM_URL}');")
        WebDriverWait(self.driver, 30).until(lambda d: len(d.window_handles) > 1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(2)

    def descargar_archivo(self, fecha, **kwargs) -> Path:
        """
        Orquesta el proceso completo de llenado de formulario, envío y descarga del reporte para una fecha específica.
        """
        try:
            # 1. Preparar fechas
            from datetime import datetime
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d") if isinstance(fecha, str) else fecha
            fecha_sistema = fecha_dt.strftime('%Y/%m/%d')
            
            # 2. Llenar fechas en el formulario
            self.fill_dates(fecha_sistema)

            # 3. Llenar campos adicionales
            self.fill_additional_fields(**kwargs)

            # 4. Enviar formulario
            self.submit_form()

            # 5. Esperar y cambiar a la nueva pestaña de resultados
            self.wait_for_results_tab()

            # 6. Verificar si hay datos
            no_data = self.check_no_data_conditions()
            if no_data:
                print(f"[{self.platform_name}] No se encontraron datos para la fecha {fecha}.")
                self.return_to_form()
                return # Salir de este proceso de fecha

            # 7. Hacer clic en el botón de descarga y esperar
            download_button_selector = (By.CLASS_NAME, "download")
            download_elem = self.driver.esperar(*download_button_selector, timeout=20)

            # Scroll al elemento antes de hacer click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_elem)
            download_elem.click()
            print(f"[{self.platform_name}] Clic en botón de descarga enviado.")

            # Esperar archivo descargado (SalesYs descarga CSV)
            archivo_descargado = self.driver.esperar_descarga(extension=".csv", timeout=60)
            
            # 8. Procesar (renombrar y mover) el archivo descargado
            self._process_file(archivo_descargado, fecha_dt, **kwargs)
            
            # 9. Regresar a la pestaña del formulario para la siguiente fecha
            self.return_to_form()

        except Exception as e:
            print(f"[{self.platform_name}] Error durante el proceso de descarga para la fecha {fecha}: {e}")
            self.return_to_form() # Intentar regresar al formulario para no bloquear el bucle
            raise

    # ====================================
    # IMPLEMENTACIÓN DE MÉTODOS ABSTRACTOS DE BaseSalesys
    # ====================================

    def get_date_field_ids(self):
        """
        Retorna los IDs de los campos de fecha 'from' y 'to' para el formulario de Estado Agente V2.
        """
        return ("from", "to") # Valores obtenidos de scr_estado_agente.py
    
    def fill_additional_fields(self, **kwargs):
        """
        Implementa el llenado de campos adicionales para el formulario de Estado Agente V2.
        Según scr_estado_agente.py, este reporte no tiene campos adicionales.
        """
        # Estado Agente no tiene campos adicionales
        pass
    
    def generate_filename(self, fecha_dt, **kwargs):
        """
        Genera el nombre del archivo para el reporte de Estado Agente V2.
        Ejemplo: "EstadoAgenteDD.xlsx"
        """
        dia = fecha_dt.strftime('%d')
        return f"EstadoAgente{dia}"

    def get_destination_paths(self, nuevo_nombre, fecha_dt, **kwargs):
        """
        Genera las rutas de destino para el archivo del reporte de Estado Agente V2.
        Por ahora, usa una ruta base simplificada.
        """
        # Simplificado para no depender de FORM_ROUTES ni form_config
        # Esto debería venir de la configuración del proyecto o ser configurable.
        
        # Ejemplo de ruta base, esto debería ser configurable (e.g., desde settings.py)
        # Por ejemplo: Z:\INFORMES\EstadoAgenteV2\ANIO\MES\
        base_path = Path("Z:/test")# Ojo: asegúrate de que esta ruta existe o se creará.

        anio = fecha_dt.year
        # Usar número de mes para evitar importar MESES_ES y mantener la simplicidad
        mes_nombre = fecha_dt.strftime('%m') 

        # Construir la ruta final
        destination_folder = base_path / self.reporte_nombre / str(anio) / mes_nombre
        
        return [destination_folder / nuevo_nombre]
