# ====================================
# SCRAPER: Salesys - RGA
# ====================================
# Scraper específico para el reporte RGA de Salesys
# Hereda login y helpers de BaseSalesys

from scrapers.sites.salesys.core.base_salesys import BaseSalesys
from selenium.webdriver.common.by import By
from pathlib import Path
import time
from config.settings import SALESYS_RGA_FORM_URL


class RGAScraper(BaseSalesys):
    """
    Scraper para el reporte RGA de Salesys.

    Hereda de BaseSalesys:
    - ✓ login() - Ya implementado (vía SessionManager)
    - ✓ _ir_a_modulo_reportes() - Helper compartido

    Solo implementa:
    - navegar_a_reporte() - Navegación específica a RGA
    - descargar_archivo() - Descarga específica de RGA

    Ventajas del SessionManager:
    - Si se ejecuta después de NominaScraper, reutiliza la misma sesión (sin login)
    """

    def __init__(self, session_manager=None):
        """
        Inicializa el scraper de RGA.

        Args:
            session_manager: SessionManager de SalesYs (opcional, se crea automáticamente)
        """
        super().__init__(reporte_nombre="RGA", session_manager=session_manager)

    # ====================================
    # IMPLEMENTACIÓN ESPECÍFICA DE RGA
    # ====================================

    def navegar_a_reporte(self):
        """Navega específicamente al reporte RGA."""
        print(f"[{self.platform_name}] Navegando a {SALESYS_RGA_FORM_URL}")
        self.driver.get(SALESYS_RGA_FORM_URL)
        # TODO: Añadir esperas (WebDriverWait) si la página tarda en cargar o necesita interacción inicial.

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
            # (PLACEHOLDER - Se necesita el ID o selector real del botón)
            download_button_selector = (By.CLASS_NAME, "download") # ¡AJUSTAR ESTE SELECTOR!
            download_elem = self.driver.esperar(*download_button_selector, timeout=20)
            download_elem.click()
            
            archivo_descargado = self.driver.esperar_descarga(extension=".xlsx", timeout=60) # Asumo .xlsx
            
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
        (PLACEHOLDER - AJUSTAR SEGÚN EL HTML DEL FORMULARIO RGA)
        """
        return ("from_rga", "to_rga") # Asunción de IDs genéricos
    
    def fill_additional_fields(self, **kwargs):
        """
        Implementa el llenado de campos adicionales para el formulario RGA.
        (PLACEHOLDER - AJUSTAR SEGÚN LOS CAMPOS ADICIONALES DEL FORMULARIO RGA)
        """
        # Por ahora, no hay campos adicionales conocidos para RGA
        pass
    
    def generate_filename(self, fecha_dt, **kwargs):
        """
        Genera el nombre del archivo para el reporte RGA.
        Ejemplo: "RGA_YYYYMMDD.xlsx"
        """
        return f"RGA_{fecha_dt.strftime('%Y%m%d')}"

    def get_destination_paths(self, nuevo_nombre, fecha_dt, **kwargs):
        """
        Genera las rutas de destino para el archivo del reporte RGA.
        Por ahora, usa una ruta base simplificada.
        (PLACEHOLDER - AJUSTAR SEGÚN LAS RUTAS DE DESTINO REALES PARA RGA)
        """
        base_path = Path("Z:/INFORMES") # Ajustar según la ruta de informes principal
        anio = fecha_dt.year
        mes_nombre = fecha_dt.strftime('%m') 

        # Construir la ruta final
        destination_folder = base_path / self.reporte_nombre / str(anio) / mes_nombre
        
        return [destination_folder / nuevo_nombre]


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

    # Es buena práctica manejar la sesión explícitamente para pruebas individuales
    session = get_salesys_session()
    try:
        scraper = RGAScraper(session_manager=session)
        scraper.ejecutar(fechas=fechas_a_procesar)
        print("\n--- Fin de la ejecución de ejemplo de RGA ---")
    except Exception as e:
        print(f"Error en la ejecución de ejemplo: {e}")
    finally:
        session.cleanup()  # Asegurar la limpieza al final de la prueba
