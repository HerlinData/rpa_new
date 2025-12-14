from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
from config.settings import SALESYS_RGA_FORM_URL, PRODUCTOS_DEFAULT
from utils.route_builder import build_destination_paths, build_filename

class RGAScraper(BaseSalesys):

    def __init__(self, productos=None, session_manager=None):
        super().__init__(reporte_nombre="rga", session_manager=session_manager)
        self.productos = productos or PRODUCTOS_DEFAULT

    @property
    def form_url(self) -> str:
        return SALESYS_RGA_FORM_URL

    def get_date_field_ids(self):
        return ("fromdate", "todate")  # IDs específicos de RGA

    def fill_additional_fields(self, producto=None, **kwargs):
        if producto:
            # Click en el dropdown de producto (Chosen.js)
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "product_chosen"))
            ).click()

            # Seleccionar el producto específico por texto
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{producto}')]"))
            ).click()

            time.sleep(0.5)  # Breve pausa para que se registre la selección

    def generate_filename(self, fecha_dt, producto=None, **kwargs):
        """Genera el nombre del archivo desde configuración YAML"""
        return build_filename(self.reporte_nombre, fecha_dt, producto=producto, **kwargs)

    def get_destination_paths(self, nuevo_nombre, fecha_dt, producto=None, **kwargs):
        """Genera las rutas de destino desde configuración YAML"""
        return build_destination_paths(self.reporte_nombre, fecha_dt, producto=producto, **kwargs)

    def _get_work_items(self, fechas, **kwargs) -> list:
        work_items = []
        for fecha in fechas:
            for producto in self.productos:
                work_items.append((fecha, producto))
        return work_items