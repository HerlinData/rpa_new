from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from pathlib import Path
from config.settings import SALESYS_ESTADO_AGENTE_V2_FORM_URL
from utils.route_builder import build_destination_paths, build_filename

class EstadoAgenteV2Scraper(BaseSalesys):

    def __init__(self, session_manager=None):
        super().__init__(reporte_nombre="estado_agente_v2", session_manager=session_manager)

    @property
    def form_url(self) -> str:
        return SALESYS_ESTADO_AGENTE_V2_FORM_URL


    def get_date_field_ids(self):
        return ("from", "to")
    
    def fill_additional_fields(self, **kwargs):
        pass

    def generate_filename(self, fecha_dt, **kwargs):
        """Genera el nombre del archivo desde configuración YAML"""
        return build_filename(self.reporte_nombre, fecha_dt, **kwargs)

    def get_destination_paths(self, nuevo_nombre, fecha_dt, **kwargs):
        """Genera las rutas de destino desde configuración YAML"""
        return build_destination_paths(self.reporte_nombre, fecha_dt, **kwargs)

    def _get_work_items(self, fechas, **kwargs) -> list:
        return fechas