from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from config.settings import ROUTES
from utils.route_builder import build_destination_paths, build_filename

class DeliveryRechazoScraper(BaseSalesys):

    def __init__(self, usuarios=None, session_manager=None):
        super().__init__(reporte_nombre="rechazo_delivery", session_manager=session_manager)

        # Usuarios a procesar desde YAML o parámetro
        config_usuarios = ROUTES.get(self.reporte_nombre, {}).get('usuarios')
        self.usuarios = usuarios or config_usuarios or ["Todo"]

    @property
    def form_url(self) -> str:
        """Lee la URL del formulario desde YAML"""
        return ROUTES.get(self.reporte_nombre, {}).get('form_url', '')

    def get_date_field_ids(self):
        """Lee los IDs de campos de fecha desde YAML"""
        date_fields = ROUTES.get(self.reporte_nombre, {}).get('date_fields', ['from', 'to'])
        return tuple(date_fields)

    def generate_filename(self, fecha_dt, **kwargs):
        """Genera el nombre del archivo desde configuración YAML"""
        return build_filename(self.reporte_nombre, fecha_dt, **kwargs)

    def get_destination_paths(self, nuevo_nombre, fecha_dt, **kwargs):
        """Genera las rutas de destino desde configuración YAML"""
        return build_destination_paths(self.reporte_nombre, fecha_dt, **kwargs)

    def _get_work_items(self, fechas, **kwargs) -> list:
        work_items = []
        for fecha in fechas:
            for usuario in self.usuarios:
                work_items.append((fecha, usuario))
        return work_items