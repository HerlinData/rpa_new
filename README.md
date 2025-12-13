# 🚀 RPA New - Guía Paso a Paso

Este proyecto usa **Nivel 2 POO** (Herencia + Polimorfismo) - el balance perfecto entre simplicidad y reutilización.

## 📁 Estructura del Proyecto

```
rpa_new/
├── config/                 # PASO 1: Configuración
│   ├── settings.py        # Configuración centralizada
│   └── .env.example       # Plantilla para credenciales
│
├── core/                   # PASO 2: Componentes core
│   └── database.py        # Conexión a SQL Server
│
├── scrapers/              # PASO 3-4: Scrapers
│   ├── base/
│   │   └── base_scraper.py      # Clase base (Template Method)
│   └── implementaciones/
│       └── salesys_scraper.py   # Ejemplo de implementación
│
├── tasks/                  # PASO 5: Orquestación (opcional)
│   └── task_interface.py  # Tareas que ejecutan scrapers
│
├── utils/                  # PASO 6: Utilidades (opcional)
│   └── selenium_helpers.py
│
├── main.py                 # PASO 7: Punto de entrada
└── requirements.txt        # Dependencias
```

---

## 🎯 Filosofía del Proyecto

### ✅ Qué ES este proyecto:
- **Nivel 2 POO**: Herencia + Polimorfismo sin sobre-ingeniería
- **Template Method Pattern**: Flujo común en clase base, detalles en subclases
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid

### ❌ Qué NO es:
- NO es arquitectura SOLID completa (eso es Nivel 3, sobre-ingeniado)
- NO tiene Factories, Registry, ni Dependency Injection
- NO tiene interfaces abstractas innecesarias

---

## 📚 Guía de Implementación Paso a Paso

### PASO 1: Configurar el proyecto

1. **Instalar dependencias:**
   ```bash
   cd rpa_new
   pip install -r requirements.txt
   ```

2. **Crear archivo .env:**
   ```bash
   cp config/.env.example .env
   # Editar .env con tus credenciales reales
   ```

3. **Verificar settings.py:**
   - Abre `config/settings.py`
   - Lee los comentarios
   - Ajusta rutas si es necesario

---

### PASO 2: Implementar DatabaseConnection

1. **Abre `core/database.py`**
2. **Busca los `TODO` y completa:**
   - `__init__`: Guardar parámetros de conexión
   - `connect()`: Crear engine de SQLAlchemy
   - `query()`: Ejecutar SELECT
   - `insert_dataframe()`: Insertar DataFrame
   - `delete_and_insert()`: DELETE + INSERT

3. **Ejemplo de implementación:**
   ```python
   def __init__(self, server, database, user=None, password=None):
       self.server = server
       self.database = database
       self.engine = None
       self.connect()

   def connect(self):
       conn_str = f"mssql+pyodbc://{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
       self.engine = create_engine(conn_str)

   def query(self, sql):
       return pd.read_sql(sql, self.engine)
   ```

4. **Probar:**
   ```python
   from core.database import DatabaseConnection
   db = DatabaseConnection("servidor", "bd")
   df = db.query("SELECT TOP 5 * FROM tabla")
   print(df)
   ```

---

### PASO 3: Entender BaseScraper

1. **Abre `scrapers/base/base_scraper.py`**
2. **Lee el flujo en `ejecutar()`:**
   ```python
   def ejecutar(self):
       self.configurar_driver()  # Configura Chrome
       self.login()              # Login (abstracto)
       self.navegar_a_reporte()  # Navega al reporte (abstracto)
       ruta = self.descargar_archivo()  # Descarga (abstracto)
       df = self.procesar_datos(ruta)   # Procesa (abstracto)
       self.guardar_en_bd(df)    # Guarda en BD (opcional)
       self.cerrar()             # Cierra navegador
   ```

3. **Completa los métodos concretos:**
   - `configurar_driver()`: Configurar Selenium WebDriver
   - `cerrar()`: Cerrar navegador

4. **NO toques los métodos `@abstractmethod`** - esos se implementan en las subclases

---

### PASO 4: Crear tu primer Scraper (Herencia)

Usaremos `SalesysScraper` como ejemplo.

1. **Abre `scrapers/implementaciones/salesys_scraper.py`**

2. **Observa cómo hereda de BaseScraper:**
   ```python
   class SalesysScraper(BaseScraper):
       def __init__(self, reporte_nombre):
           super().__init__(platform_name="Salesys")
           self.reporte_nombre = reporte_nombre
   ```

3. **Implementa los métodos abstractos uno por uno:**

   **a) `login()`:**
   ```python
   def login(self):
       self.driver.get("https://salesys.example.com/login")
       self.driver.find_element(By.ID, "username").send_keys(SALESYS_USER)
       self.driver.find_element(By.ID, "password").send_keys(SALESYS_PASS)
       self.driver.find_element(By.ID, "login-btn").click()
       time.sleep(3)
   ```

   **b) `navegar_a_reporte()`:**
   ```python
   def navegar_a_reporte(self):
       self.driver.find_element(By.LINK_TEXT, "Reportes").click()
       self.driver.find_element(By.LINK_TEXT, self.reporte_nombre).click()
       time.sleep(2)
   ```

   **c) `descargar_archivo()`:**
   ```python
   def descargar_archivo(self):
       self.driver.find_element(By.ID, "btn-download").click()
       time.sleep(5)
       return DOWNLOADS_DIR / f"{self.reporte_nombre}.xlsx"
   ```

   **d) `procesar_datos()`:**
   ```python
   def procesar_datos(self, ruta_archivo):
       df = pd.read_excel(ruta_archivo)
       df = df.dropna()
       # Aplicar transformaciones específicas
       return df
   ```

4. **Probar el scraper:**
   ```python
   scraper = SalesysScraper("RGA")
   df = scraper.ejecutar()  # Usa el flujo de BaseScraper automáticamente
   ```

---

### PASO 5: Crear más Scrapers (Polimorfismo)

Ahora crea scrapers para otras plataformas siguiendo el mismo patrón:

1. **GenesysScraper:**
   ```bash
   # Crear archivo
   touch scrapers/implementaciones/genesys_scraper.py
   ```

2. **Copiar estructura de SalesysScraper**

3. **Implementar métodos específicos de Genesys:**
   - `login()` → Login de Genesys
   - `navegar_a_reporte()` → Navegación específica
   - `descargar_archivo()` → Descarga de Genesys
   - `procesar_datos()` → Procesamiento específico

4. **El flujo `ejecutar()` es el mismo** - heredado de BaseScraper

---

### PASO 6: Orquestar con Tasks (Opcional)

Si necesitas ejecutar múltiples scrapers:

1. **Abre `tasks/task_interface.py`**

2. **Implementa `SalesysReportTask.execute()`:**
   ```python
   def execute(self):
       from scrapers.implementaciones.salesys_scraper import SalesysScraper

       scraper = SalesysScraper(self.reporte_nombre)
       df = scraper.ejecutar()

       return {
           'status': 'success',
           'reporte': self.reporte_nombre,
           'registros': len(df),
           'data': df
       }
   ```

3. **Crear más tasks:**
   - `GenesysReportTask`
   - `ConsolidacionTask` (que combine varios scrapers)

---

### PASO 7: Ejecutar desde main.py

1. **Abre `main.py`**

2. **Implementa ejecución de tareas:**
   ```python
   def main():
       # Ejecutar Salesys RGA
       task_rga = SalesysReportTask("RGA")
       resultado_rga = task_rga.run()

       # Ejecutar Salesys Nómina
       task_nomina = SalesysReportTask("Nomina")
       resultado_nomina = task_nomina.run()

       # Mostrar resumen
       print(f"RGA: {resultado_rga['registros']} registros")
       print(f"Nómina: {resultado_nomina['registros']} registros")
   ```

3. **Ejecutar:**
   ```bash
   python main.py
   ```

---

## 🎓 Conceptos Clave

### 1. Template Method Pattern
```python
# BaseScraper define el FLUJO (template)
def ejecutar(self):
    self.login()              # ← Cada subclase implementa
    self.navegar_a_reporte()  # ← Cada subclase implementa
    self.descargar_archivo()  # ← Cada subclase implementa
```

### 2. Herencia
```python
# SalesysScraper HEREDA el flujo de BaseScraper
class SalesysScraper(BaseScraper):
    # Solo implementa los detalles específicos
```

### 3. Polimorfismo
```python
# Puedes tratar todos los scrapers igual
scrapers = [
    SalesysScraper("RGA"),
    GenesysScraper("Ocupacion"),
    NavicatScraper("Reporte1")
]

for scraper in scrapers:
    scraper.ejecutar()  # Cada uno ejecuta su propia implementación
```

---

## 🔄 Comparación con Proyecto Anterior

### ❌ Antes (RPA_/ - Nivel 3 SOLID):
- 80+ archivos para entender
- Factories, Registry, Interfaces abstractas
- Difícil de mantener para equipos pequeños

### ✅ Ahora (RPA_new/ - Nivel 2 POO):
- ~10 archivos principales
- Herencia simple + Template Method
- Fácil de entender y extender

---

## 📝 Checklist de Progreso

- [ ] PASO 1: Configuración y .env
- [ ] PASO 2: DatabaseConnection implementado
- [ ] PASO 3: BaseScraper completado
- [ ] PASO 4: Primer scraper (Salesys) funcionando
- [ ] PASO 5: Segundo scraper (Genesys/otro)
- [ ] PASO 6: Tasks implementadas (opcional)
- [ ] PASO 7: main.py ejecutando todo

---

## 🚨 Errores Comunes

1. **Olvidar llamar `super().__init__()`:**
   ```python
   # ❌ MAL
   def __init__(self):
       self.nombre = "Salesys"

   # ✅ BIEN
   def __init__(self):
       super().__init__(platform_name="Salesys")
   ```

2. **Sobreescribir `ejecutar()`:**
   ```python
   # ❌ MAL - NO sobreescribas ejecutar()
   def ejecutar(self):
       # código personalizado

   # ✅ BIEN - Solo implementa los métodos abstractos
   def login(self):
       # tu implementación
   ```

3. **Hardcodear credenciales:**
   ```python
   # ❌ MAL
   user = "mi_usuario"

   # ✅ BIEN
   from config.settings import SALESYS_USER
   ```

---

## 💡 Próximos Pasos

Después de completar los 7 pasos:

1. **Agregar más scrapers** usando el mismo patrón
2. **Agregar logging** para debugging
3. **Agregar manejo de errores** más robusto
4. **Agregar tests** (pytest) cuando sea necesario

---

## 📞 Recursos

- **REFACTORING_PROGRESS.md**: Lecciones aprendidas del proyecto anterior
- **ARCHITECTURE.md**: Explicación de la arquitectura (si existe)
- **Template Method Pattern**: [Refactoring Guru](https://refactoring.guru/design-patterns/template-method)

---

**Última actualización:** 2025-12-12
**Nivel de complejidad:** Intermedio (Nivel 2 POO)
**Tiempo estimado:** Completar PASO 1-4 te da un scraper funcional
