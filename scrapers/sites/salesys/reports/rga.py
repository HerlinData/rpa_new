from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from config.settings import ROUTES
from utils.route_builder import build_destination_paths, build_filename

class RGAScraper(BaseSalesys):

    def __init__(self, productos=None, session_manager=None):
        super().__init__(reporte_nombre="rga", session_manager=session_manager)

        # Obtener configuración del reporte
        config = ROUTES.get(self.reporte_nombre, {})

        # Obtener opciones disponibles desde archivos
        opciones_disponibles = list(config.get('archivos', {}).keys())

        # Validar que se hayan especificado productos
        if not productos:
            raise ValueError(
                f"[{self.reporte_nombre}] Debe especificar productos. "
                f"Opciones disponibles: {opciones_disponibles}"
            )

        # Validar que los productos existan en la configuración
        invalidos = [p for p in productos if p not in opciones_disponibles]
        if invalidos:
            raise ValueError(
                f"[{self.reporte_nombre}] Productos inválidos: {invalidos}. "
                f"Opciones disponibles: {opciones_disponibles}"
            )

        self.productos = productos

    @property
    def form_url(self) -> str:
        """Lee la URL del formulario desde YAML"""
        return ROUTES.get(self.reporte_nombre, {}).get('form_url', '')

    def get_date_field_ids(self):
        """Lee los IDs de campos de fecha desde YAML"""
        date_fields = ROUTES.get(self.reporte_nombre, {}).get('date_fields', ['fromdate', 'todate'])
        return tuple(date_fields)

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