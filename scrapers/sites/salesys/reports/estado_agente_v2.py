from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from pathlib import Path
from config.settings import SALESYS_ESTADO_AGENTE_V2_FORM_URL

class EstadoAgenteV2Scraper(BaseSalesys):

    def __init__(self, session_manager=None):
        super().__init__(reporte_nombre="EstadoAgenteV2", session_manager=session_manager)

    @property
    def form_url(self) -> str:
        return SALESYS_ESTADO_AGENTE_V2_FORM_URL


    def get_date_field_ids(self):
        return ("from", "to")
    
    def fill_additional_fields(self, **kwargs):
        pass
    
    def generate_filename(self, fecha_dt, **kwargs):
        dia = fecha_dt.strftime('%d')
        return f"EstadoAgente{dia}"

    def get_destination_paths(self, nuevo_nombre, fecha_dt, **kwargs):
        """
        Genera las rutas de destino para el archivo del reporte de Estado Agente V2.
        """
        base_path = Path("Z:/test")# Ojo: asegúrate de que esta ruta existe o se creará.

        anio = fecha_dt.year
        # Usar número de mes para evitar importar MESES_ES y mantener la simplicidad
        mes_nombre = fecha_dt.strftime('%m') 

        # Construir la ruta final
        destination_folder = base_path / self.reporte_nombre / str(anio) / mes_nombre
        
        return [destination_folder / nuevo_nombre]

    def _get_work_items(self, fechas, **kwargs) -> list:
        return fechas