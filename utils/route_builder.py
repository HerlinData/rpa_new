# ====================================
# CONSTRUCTOR DE RUTAS DESDE YAML
# ====================================
from pathlib import Path
from config.settings import FILE_ROUTES, MESES_ES

# Base path oficial para todas las descargas
BASE_PATH = Path("Z:/DESCARGA INFORMES")


def build_destination_paths(reporte_nombre, fecha_dt, producto=None, **kwargs):
    """
    Construye rutas de destino desde configuración YAML (file_routes.yaml).

    Args:
        reporte_nombre: Nombre del reporte (ej: "estado_agente_v2", "rga")
        fecha_dt: datetime object
        producto: Producto (solo para RGA y reportes con múltiples productos)

    Returns:
        Lista de Path objects con las rutas completas de destino
    """
    # Obtener configuración del reporte
    config = FILE_ROUTES.get(reporte_nombre)

    if not config:
        print(f"[WARNING] No hay configuración YAML para '{reporte_nombre}'")
        # Fallback a ruta genérica
        return [BASE_PATH / reporte_nombre / f"{fecha_dt.year}" / f"{fecha_dt.month:02d}"]

    # Variables disponibles para reemplazo
    variables = {
        'year': str(fecha_dt.year),
        'month': MESES_ES[fecha_dt.month],  # Nombre del mes en español
        'day': fecha_dt.strftime('%d'),
    }

    # Variables específicas para productos
    if producto:
        variables['product'] = producto.upper()
        variables['product_lower'] = producto.lower()

    # Generar nombre de archivo
    filename_template = config.get('filename', 'archivo')
    extension = config.get('extension', '.csv')
    filename = filename_template.format(**variables) + extension

    # Construir rutas de destino
    rutas_destino = []

    # Caso 1: Reporte simple con lista 'rutas' (ej: estado_agente_v2)
    if 'rutas' in config:
        for ruta_template in config['rutas']:
            ruta_relativa = ruta_template.format(**variables)
            ruta_completa = BASE_PATH / ruta_relativa / filename
            rutas_destino.append(ruta_completa)

    # Caso 2: Reporte con archivos por producto (ej: rga)
    elif 'archivos' in config:
        if producto and producto in config['archivos']:
            for ruta_template in config['archivos'][producto]:
                ruta_relativa = ruta_template.format(**variables)
                ruta_completa = BASE_PATH / ruta_relativa / filename
                rutas_destino.append(ruta_completa)
        else:
            print(f"[WARNING] No hay configuración para producto '{producto}' en '{reporte_nombre}'")

    return rutas_destino


def build_filename(reporte_nombre, fecha_dt, producto=None, **kwargs):
    """
    Construye nombre de archivo desde configuración YAML.

    Args:
        reporte_nombre: Nombre del reporte
        fecha_dt: datetime object
        producto: Producto (opcional)

    Returns:
        String con el nombre del archivo incluyendo extensión
    """
    config = FILE_ROUTES.get(reporte_nombre, {})

    variables = {
        'day': fecha_dt.strftime('%d'),
        'month': MESES_ES[fecha_dt.month],
        'year': str(fecha_dt.year),
    }

    if producto:
        variables['product_lower'] = producto.lower()
        variables['product'] = producto.upper()

    filename_template = config.get('filename', 'archivo')
    extension = config.get('extension', '.csv')

    return filename_template.format(**variables) + extension
