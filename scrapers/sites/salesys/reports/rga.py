# ====================================
# SCRAPER: Salesys - RGA
# ====================================
# Scraper específico para el reporte RGA de Salesys
# Hereda login y helpers de BaseSalesys
# PARTICULARIDAD: Descarga múltiples productos por cada fecha

from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
from config.settings import SALESYS_RGA_FORM_URL, PRODUCTOS_DEFAULT


class RGAScraper(BaseSalesys):
    """
    Scraper para el reporte RGA de Salesys.

    PARTICULARIDAD: Descarga múltiples productos por cada fecha.
    Por ejemplo, para fecha 2025-12-13 descarga:
    - CLARO -> claro13.csv
    - TIGO -> tigo13.csv

    Hereda de BaseSalesys:
    - ✓ login() - Ya implementado (vía SessionManager)
    - ✓ _ir_a_modulo_reportes() - Helper compartido

    Solo implementa:
    - navegar_a_reporte() - Navegación específica a RGA
    - descargar_archivo() - Descarga específica de RGA con selección de producto
    - ejecutar() - Sobrescrito para iterar productos x fechas

    Ventajas del SessionManager:
    - Si se ejecuta después de EstadoAgente, reutiliza la misma sesión (sin login)
    """

    def __init__(self, productos=None, session_manager=None):
        """
        Inicializa el scraper de RGA.

        Args:
            productos: Lista de productos a descargar (default: PRODUCTOS_DEFAULT de settings)
            session_manager: SessionManager de SalesYs (opcional, se crea automáticamente)
        """
        super().__init__(reporte_nombre="RGA", session_manager=session_manager)
        self.productos = productos or PRODUCTOS_DEFAULT

    # ====================================
    # IMPLEMENTACIÓN ESPECÍFICA DE RGA
    # ====================================

    def navegar_a_reporte(self):
        """Navega específicamente al reporte RGA."""
        print(f"[{self.platform_name}] Navegando a {SALESYS_RGA_FORM_URL}")

        # Abrir formulario en nueva pestaña (como el código original)
        from selenium.webdriver.support.ui import WebDriverWait

        self.driver.execute_script(f"window.open('{SALESYS_RGA_FORM_URL}');")
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
        Retorna los IDs de los campos de fecha 'from' y 'to' para el formulario RGA.
        """
        return ("fromdate", "todate")  # IDs específicos de RGA

    def fill_additional_fields(self, producto=None, **kwargs):
        """
        Implementa el llenado de campos adicionales para el formulario RGA.

        PARTICULARIDAD: RGA requiere seleccionar un PRODUCTO en un dropdown.
        El dropdown usa Chosen.js con ID "product_chosen".
        """
        if producto:
            # Click en el dropdown de producto (Chosen.js)
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "product_chosen"))
            ).click()

            # Seleccionar el producto específico por texto
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{producto}')]"))
            ).click()

            print(f"[{self.platform_name}] Producto seleccionado: {producto}")
            time.sleep(0.5)  # Breve pausa para que se registre la selección

    def generate_filename(self, fecha_dt, producto=None, **kwargs):
        """
        Genera el nombre del archivo para el reporte RGA.

        Formato: {producto_lowercase}{DD}
        Ejemplos:
            - CLARO + 2025-12-13 → claro13
            - TIGO + 2025-12-13 → tigo13
        """
        dia = fecha_dt.strftime('%d')
        if producto:
            return f"{producto.lower()}{dia}"
        else:
            return f"rga{dia}"

    def get_destination_paths(self, nuevo_nombre, fecha_dt, producto=None, **kwargs):
        """
        Genera las rutas de destino para el archivo del reporte RGA.
        """
        base_path = Path("Z:/test")
        anio = fecha_dt.year
        mes_nombre = fecha_dt.strftime('%m')  # Número de mes: 01, 02, etc.

        # Si hay producto, crear subcarpeta por producto
        if producto:
            destination_folder = base_path / self.reporte_nombre / producto.upper() / str(anio) / mes_nombre
        else:
            destination_folder = base_path / self.reporte_nombre / str(anio) / mes_nombre

        return [destination_folder / nuevo_nombre]

    # ====================================
    # SOBRESCRITURA DE EJECUTAR PARA MÚLTIPLES PRODUCTOS
    # ====================================

    def ejecutar(self, fechas):
        """
        Sobrescribe el método ejecutar() de BaseScraper para manejar múltiples productos.

        Flujo:
            1. Configurar driver y login (una vez)
            2. Navegar al reporte (una vez)
            3. Para cada FECHA:
                a. Para cada PRODUCTO:
                    - Llenar formulario (fecha + producto)
                    - Descargar archivo
                    - Procesar y mover archivo
                    - Volver al formulario

        Ejemplo de salida:
            Fecha 2025-12-13:
                → CLARO: claro13.csv
                → TIGO: tigo13.csv
            Fecha 2025-12-12:
                → CLARO: claro12.csv
                → TIGO: tigo12.csv
        """
        print(f"[{self.platform_name}] Iniciando scraper...")

        # 1. Configurar driver
        self.configurar_driver()

        # 2. Login (ya manejado por SessionManager)
        self.login()

        # 3. Navegar al reporte
        self.navegar_a_reporte()

        # 4. Procesar cada fecha
        for fecha in fechas:
            print(f"\n--- Procesando fecha: {fecha} ---")

            # 5. Para cada producto
            for producto in self.productos:
                print(f"   [PRODUCTO: {producto}]")

                try:
                    # Pasar el producto como parámetro adicional
                    self.descargar_archivo(fecha, producto=producto)
                    print(f"   ✓ {producto} completado")

                except Exception as e:
                    print(f"   ✗ Error procesando {producto}: {e}")

        # 6. Cerrar (no cierra driver, lo maneja SessionManager)
        self.cerrar()

        print(f"[{self.platform_name}] ✓ Proceso completado para todas las fechas y productos.")


# ====================================
# EJEMPLO DE USO
# ====================================
if __name__ == "__main__":
    from scrapers.sites.salesys.core.session_manager import get_salesys_session
    from datetime import date, timedelta

    # --- Definir el rango de fechas a procesar ---
    # Ejemplo: procesar los últimos 2 días
    hoy = date.today()
    fechas_a_procesar = [(hoy - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(2)]

    print(f"--- Ejemplo de ejecución individual para RGA ---")
    print(f"Rango de fechas a procesar: {fechas_a_procesar}")
    print(f"Productos a procesar: {PRODUCTOS_DEFAULT}")

    # Es buena práctica manejar la sesión explícitamente para pruebas individuales
    session = get_salesys_session()
    try:
        # Opción 1: Usar productos por defecto
        scraper = RGAScraper(session_manager=session)

        # Opción 2: Especificar productos custom
        # scraper = RGAScraper(productos=["CLARO", "TIGO", "MOVISTAR"], session_manager=session)

        scraper.ejecutar(fechas=fechas_a_procesar)
        print("\n--- Fin de la ejecución de ejemplo de RGA ---")
    except Exception as e:
        print(f"Error en la ejecución de ejemplo: {e}")
    finally:
        session.cleanup()  # Asegurar la limpieza al final de la prueba
