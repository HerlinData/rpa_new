# ⚡ Inicio Rápido - 5 Minutos

Esta guía te lleva desde cero hasta tu primer scraper funcionando en ~5 minutos.

---

## 🎯 Objetivo
Entender cómo funciona el sistema implementando un scraper simple paso a paso.

---

## 📋 Pre-requisitos
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear archivo .env
cp config/.env.example .env

# 3. Editar .env con tus credenciales (usa un editor de texto)
# SALESYS_USER=tu_usuario
# SALESYS_PASS=tu_password
# DB_SERVER=tu_servidor
# etc.
```

---

## 🚀 Paso 1: Completar DatabaseConnection (5 min)

Abre `core/database.py` y busca los `TODO`. Implementa este código:

```python
from sqlalchemy import create_engine, text
import pandas as pd


class DatabaseConnection:
    def __init__(self, server: str, database: str, user: str = None, password: str = None):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.engine = None
        self.connect()

    def connect(self):
        if self.user and self.password:
            conn_str = f"mssql+pyodbc://{self.user}:{self.password}@{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            # Windows Authentication
            conn_str = f"mssql+pyodbc://{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

        self.engine = create_engine(conn_str)

    def query(self, sql: str) -> pd.DataFrame:
        return pd.read_sql(sql, self.engine)

    def execute(self, sql: str):
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()

    def insert_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)

    def delete_and_insert(self, df: pd.DataFrame, table_name: str, condition: str):
        delete_sql = f"DELETE FROM {table_name} {condition}"
        self.execute(delete_sql)
        self.insert_dataframe(df, table_name)

    def close(self):
        if self.engine:
            self.engine.dispose()
```

---

## 🚀 Paso 2: Completar BaseScraper (5 min)

Abre `scrapers/base/base_scraper.py` y completa estos métodos:

```python
from selenium.webdriver.chrome.options import Options

def configurar_driver(self):
    options = Options()
    options.add_argument("--start-maximized")
    # Descomentar siguiente línea para modo headless (sin interfaz)
    # options.add_argument("--headless")

    self.driver = webdriver.Chrome(options=options)
    print(f"[{self.platform_name}] Chrome configurado")

def cerrar(self):
    if self.driver:
        self.driver.quit()
        print(f"[{self.platform_name}] Chrome cerrado")
```

---

## 🚀 Paso 3: Implementar SalesysScraper (10 min)

Abre `scrapers/implementaciones/salesys_scraper.py`. Aquí hay un ejemplo básico:

```python
from scrapers.base.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from pathlib import Path
from config.settings import SALESYS_USER, SALESYS_PASS, DOWNLOADS_DIR
import time


class SalesysScraper(BaseScraper):
    def __init__(self, reporte_nombre: str):
        super().__init__(platform_name="Salesys")
        self.reporte_nombre = reporte_nombre

    def login(self):
        # AJUSTA ESTAS LÍNEAS CON LOS SELECTORES REALES DE TU PLATAFORMA
        self.driver.get("https://tu-salesys-url.com/login")

        # Esperar a que cargue la página
        time.sleep(2)

        # Encontrar campos (AJUSTAR SEGÚN TU HTML)
        username_field = self.driver.find_element(By.NAME, "username")  # Cambiar selector
        password_field = self.driver.find_element(By.NAME, "password")  # Cambiar selector

        # Ingresar credenciales
        username_field.send_keys(SALESYS_USER)
        password_field.send_keys(SALESYS_PASS)

        # Click en login (AJUSTAR SELECTOR)
        login_button = self.driver.find_element(By.ID, "login-btn")  # Cambiar selector
        login_button.click()

        # Esperar a que cargue dashboard
        time.sleep(3)
        print(f"[{self.platform_name}] Login exitoso")

    def navegar_a_reporte(self):
        # AJUSTAR SEGÚN TU PLATAFORMA
        reportes_menu = self.driver.find_element(By.LINK_TEXT, "Reportes")
        reportes_menu.click()
        time.sleep(1)

        reporte_link = self.driver.find_element(By.LINK_TEXT, self.reporte_nombre)
        reporte_link.click()
        time.sleep(2)
        print(f"[{self.platform_name}] Navegado a {self.reporte_nombre}")

    def descargar_archivo(self) -> Path:
        # AJUSTAR SEGÚN TU PLATAFORMA
        download_btn = self.driver.find_element(By.ID, "btn-download")
        download_btn.click()

        # Esperar descarga (mejor: implementar espera inteligente)
        time.sleep(5)

        # Asumir que se descargó como reportename.xlsx
        archivo = DOWNLOADS_DIR / f"{self.reporte_nombre}.xlsx"
        print(f"[{self.platform_name}] Archivo descargado: {archivo}")
        return archivo

    def procesar_datos(self, ruta_archivo: Path) -> pd.DataFrame:
        # Leer archivo
        df = pd.read_excel(ruta_archivo)

        # Limpiar datos
        df = df.dropna()  # Eliminar filas vacías

        # Ejemplo: Renombrar columnas
        # df = df.rename(columns={'Col Vieja': 'col_nueva'})

        # Ejemplo: Agregar columna de fecha
        # df['fecha_proceso'] = datetime.now()

        print(f"[{self.platform_name}] Datos procesados: {len(df)} registros")
        return df

    def guardar_en_bd(self, df: pd.DataFrame):
        # OPCIONAL: Descomentar si quieres guardar en BD
        """
        from core.database import DatabaseConnection
        from config.settings import DB_SERVER, DB_NAME

        db = DatabaseConnection(server=DB_SERVER, database=DB_NAME)

        # Ejemplo: Borrar datos del mes actual e insertar nuevos
        mes_actual = datetime.now().month
        year_actual = datetime.now().year
        condition = f"WHERE mes = {mes_actual} AND year = {year_actual}"

        db.delete_and_insert(df, "tabla_salesys", condition)
        db.close()

        print(f"[{self.platform_name}] Guardado en BD exitosamente")
        """
        print(f"[{self.platform_name}] Guardado en BD omitido (implementar si necesario)")
```

---

## 🚀 Paso 4: Probar el Scraper (2 min)

Crea un archivo `test_scraper.py` en la raíz:

```python
# test_scraper.py
from scrapers.implementaciones.salesys_scraper import SalesysScraper


def main():
    print("\n" + "="*60)
    print("Probando SalesysScraper")
    print("="*60 + "\n")

    # Crear scraper
    scraper = SalesysScraper(reporte_nombre="RGA")

    # Ejecutar (usa el flujo de BaseScraper automáticamente)
    try:
        df = scraper.ejecutar()

        # Mostrar resultados
        print(f"\n✓ Scraper completado exitosamente")
        print(f"Registros obtenidos: {len(df)}")
        print(f"\nPrimeras 5 filas:")
        print(df.head())

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    main()
```

Ejecutar:
```bash
python test_scraper.py
```

---

## 🎓 Lo que acabas de aprender

1. **Template Method Pattern**:
   - `BaseScraper.ejecutar()` define el flujo
   - `SalesysScraper` solo implementa los detalles

2. **Herencia**:
   - `SalesysScraper` hereda todo de `BaseScraper`
   - No necesitas reescribir el método `ejecutar()`

3. **Separación de responsabilidades**:
   - `DatabaseConnection` → maneja BD
   - `BaseScraper` → maneja flujo común
   - `SalesysScraper` → maneja lógica específica

---

## 🔄 Próximos Pasos

### 1. Crear otro scraper (Genesys, Navicat, etc.)

```bash
# Crear archivo
touch scrapers/implementaciones/genesys_scraper.py
```

Copiar estructura de `SalesysScraper` y ajustar:
- `login()` → Login de Genesys
- `navegar_a_reporte()` → Navegación de Genesys
- `descargar_archivo()` → Descarga de Genesys
- `procesar_datos()` → Procesamiento específico

### 2. Usar Tasks para orquestar

```python
# main.py
from tasks.task_interface import SalesysReportTask

task_rga = SalesysReportTask("RGA")
resultado = task_rga.run()

task_nomina = SalesysReportTask("Nomina")
resultado = task_nomina.run()
```

### 3. Agregar manejo de errores robusto

### 4. Agregar logging

### 5. Parametrizar fechas y filtros

---

## 🐛 Troubleshooting Común

### Error: "No module named 'selenium'"
```bash
pip install selenium
```

### Error: Chrome driver not found
```bash
# Descargar ChromeDriver de:
# https://chromedriver.chromium.org/
# O instalar con:
pip install webdriver-manager
```

### Error: No se puede conectar a la BD
- Verificar `DB_SERVER` y `DB_NAME` en `.env`
- Verificar que el servidor SQL esté corriendo
- Verificar driver ODBC instalado

### El scraper no encuentra elementos
- Usar herramientas de desarrollo del navegador (F12)
- Verificar selectores (ID, NAME, XPATH)
- Agregar `time.sleep()` para esperar carga de página
- Usar `WebDriverWait` para esperas inteligentes

---

## 📚 Recursos

- **README.md**: Guía completa con 7 pasos detallados
- **FLUJO_VISUAL.md**: Diagramas del flujo y arquitectura
- **REFACTORING_PROGRESS.md**: Lecciones del proyecto anterior

---

**¿Listo para más?** Lee el **README.md** completo para entender la arquitectura en profundidad.

**¿Tienes dudas?** Revisa **FLUJO_VISUAL.md** para ver diagramas del flujo.
