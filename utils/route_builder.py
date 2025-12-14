# ====================================
# CONSTRUCTOR DE RUTAS DESDE YAML
# ====================================
from pathlib import Path
from config.settings import ROUTES, MESES_ES, BASE_OUTPUT_PATH

# Usar BASE_PATH desde settings (configurado en .env)
BASE_PATH = Path(BASE_OUTPUT_PATH)


def build_destination_paths(reporte_nombre, fecha_dt, producto=None, usuario=None, **kwargs):
    """
    Construye rutas de destino desde configuración YAML (file_routes.yaml).

    Args:
        reporte_nombre: Nombre del reporte (ej: "estado_agente_v2", "rga")
        fecha_dt: datetime object
        producto: Producto (solo para RGA y reportes con múltiples productos)
        usuario: Usuario (solo para reportes con múltiples usuarios)

    Returns:
        Lista de Path objects con las rutas completas de destino
    """
    # Obtener configuración del reporte
    config = ROUTES.get(reporte_nombre)

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

    # Variables específicas para usuarios
    if usuario:
        variables['usuario'] = usuario
        variables['usuario_lower'] = usuario.lower()

    # Construir rutas de destino
    rutas_destino = []

    # Caso 1: Reporte simple con lista 'rutas' (ej: estado_agente_v2)
    if 'rutas' in config:
        filename_template = config.get('filename', 'archivo')
        extension = config.get('extension', '.csv')
        filename = filename_template.format(**variables) + extension

        for ruta_template in config['rutas']:
            ruta_relativa = ruta_template.format(**variables)
            ruta_completa = BASE_PATH / ruta_relativa / filename
            rutas_destino.append(ruta_completa)

    # Caso 2: Reporte con archivos por producto o usuario (ej: rga, rechazo_delivery)
    elif 'archivos' in config:
        # Determinar la clave a buscar (producto o usuario)
        clave = producto or usuario
        tipo = "producto" if producto else "usuario"

        if clave and clave in config['archivos']:
            item_config = config['archivos'][clave]

            # Leer filename específico del producto/usuario
            filename_template = item_config.get('filename', clave.lower())
            extension = config.get('extension', '.csv')
            filename = filename_template.format(**variables) + extension

            # Leer rutas del producto/usuario
            rutas_item = item_config.get('rutas', [])
            for ruta_template in rutas_item:
                ruta_relativa = ruta_template.format(**variables)
                ruta_completa = BASE_PATH / ruta_relativa / filename
                rutas_destino.append(ruta_completa)
        else:
            print(f"[WARNING] No hay configuración para {tipo} '{clave}' en '{reporte_nombre}'")

    return rutas_destino


def build_filename(reporte_nombre, fecha_dt, producto=None, usuario=None, **kwargs):
    """
    Construye nombre de archivo desde configuración YAML.

    Args:
        reporte_nombre: Nombre del reporte
        fecha_dt: datetime object
        producto: Producto (opcional)
        usuario: Usuario (opcional)

    Returns:
        String con el nombre del archivo incluyendo extensión
    """
    config = ROUTES.get(reporte_nombre, {})

    variables = {
        'day': fecha_dt.strftime('%d'),
        'month': MESES_ES[fecha_dt.month],
        'year': str(fecha_dt.year),
    }

    if producto:
        variables['product_lower'] = producto.lower()
        variables['product'] = producto.upper()

    if usuario:
        variables['usuario'] = usuario
        variables['usuario_lower'] = usuario.lower()

    # Si hay archivos por producto o usuario, leer filename específico
    clave = producto or usuario
    if 'archivos' in config and clave and clave in config['archivos']:
        filename_template = config['archivos'][clave].get('filename', clave.lower())
    else:
        filename_template = config.get('filename', 'archivo')

    extension = config.get('extension', '.csv')

    return filename_template.format(**variables) + extension
