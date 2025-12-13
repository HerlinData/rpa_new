# ====================================
# PASO 4: EJEMPLO DE IMPLEMENTACIÓN
# ====================================
# Esta es una implementación concreta de BaseScraper para Salesys
# Demuestra cómo heredar y solo implementar los métodos específicos

from scrapers.base.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from pathlib import Path
from config.settings import SALESYS_USER, SALESYS_PASS, DOWNLOADS_DIR
import time


class SalesysScraper(BaseScraper):
    """
    Scraper específico para la plataforma Salesys.

    Hereda el flujo completo de BaseScraper.
    Solo implementa los métodos específicos de Salesys.
    """

    def __init__(self, reporte_nombre: str):
        """
        Args:
            reporte_nombre: Nombre del reporte a descargar (ej: "RGA", "Nomina")
        """
        super().__init__(platform_name="Salesys")
        self.reporte_nombre = reporte_nombre

    # ====================================
    # IMPLEMENTACIÓN DE MÉTODOS ABSTRACTOS
    # ====================================

    def login(self):
        """
        TODO: Implementar login específico de Salesys

        Pasos sugeridos:
        1. Navegar a URL de login
        2. Encontrar campos usuario/contraseña
        3. Ingresar credenciales desde config.settings
        4. Click en botón login
        5. Esperar a que cargue dashboard
        """
        # Ejemplo:
        # self.driver.get("https://salesys.example.com/login")
        # self.driver.find_element(By.ID, "username").send_keys(SALESYS_USER)
        # self.driver.find_element(By.ID, "password").send_keys(SALESYS_PASS)
        # self.driver.find_element(By.ID, "login-btn").click()
        # WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "dashboard"))
        # )
        print(f"[{self.platform_name}] TODO: Implementar login")

    def navegar_a_reporte(self):
        """
        TODO: Navegar al reporte específico

        Pasos sugeridos:
        1. Click en menú "Reportes"
        2. Seleccionar el reporte según self.reporte_nombre
        3. Esperar a que cargue formulario
        """
        # Ejemplo:
        # self.driver.find_element(By.LINK_TEXT, "Reportes").click()
        # self.driver.find_element(By.LINK_TEXT, self.reporte_nombre).click()
        # time.sleep(2)
        print(f"[{self.platform_name}] TODO: Navegar a {self.reporte_nombre}")

    def descargar_archivo(self) -> Path:
        """
        TODO: Descargar el archivo Excel/CSV

        Pasos sugeridos:
        1. Seleccionar fechas/filtros si es necesario
        2. Click en botón "Descargar" o "Exportar"
        3. Esperar a que se complete la descarga
        4. Retornar la ruta del archivo descargado

        Returns:
            Path al archivo descargado
        """
        # Ejemplo:
        # self.driver.find_element(By.ID, "btn-download").click()
        # time.sleep(5)  # Esperar descarga
        # archivo = DOWNLOADS_DIR / f"{self.reporte_nombre}.xlsx"
        # return archivo
        print(f"[{self.platform_name}] TODO: Descargar archivo")
        return DOWNLOADS_DIR / "ejemplo.xlsx"

    def procesar_datos(self, ruta_archivo: Path) -> pd.DataFrame:
        """
        TODO: Procesar el archivo descargado

        Pasos sugeridos:
        1. Leer archivo Excel/CSV con pandas
        2. Limpiar datos (renombrar columnas, eliminar vacíos, etc.)
        3. Aplicar transformaciones necesarias
        4. Retornar DataFrame limpio

        Args:
            ruta_archivo: Path al archivo descargado

        Returns:
            DataFrame procesado
        """
        # Ejemplo:
        # df = pd.read_excel(ruta_archivo)
        # df = df.dropna()
        # df = df.rename(columns={'Col Vieja': 'col_nueva'})
        # return df
        print(f"[{self.platform_name}] TODO: Procesar {ruta_archivo}")
        return pd.DataFrame()  # DataFrame vacío por ahora

    def guardar_en_bd(self, df: pd.DataFrame):
        """
        TODO OPCIONAL: Guardar datos en base de datos

        Pasos sugeridos:
        1. Importar DatabaseConnection
        2. Conectar a BD
        3. Borrar registros antiguos (si aplica)
        4. Insertar nuevos datos

        Args:
            df: DataFrame a guardar
        """
        # Ejemplo:
        # from core.database import DatabaseConnection
        # db = DatabaseConnection(server=DB_SERVER, database=DB_NAME)
        # db.delete_and_insert(df, "tabla_salesys", "WHERE mes = 12")
        print(f"[{self.platform_name}] TODO: Guardar en BD")


# ====================================
# EJEMPLO DE USO
# ====================================
if __name__ == "__main__":
    # Crear instancia del scraper
    scraper = SalesysScraper(reporte_nombre="RGA")

    # Ejecutar (usa el flujo de BaseScraper automáticamente)
    df_resultado = scraper.ejecutar()

    # Opcionalmente trabajar con el DataFrame retornado
    print(df_resultado.head())
