# 📊 Flujo Visual del Sistema

## 🎯 Arquitectura General (Nivel 2 POO)

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│              (Punto de entrada principal)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 tasks/task_interface.py                 │
│            (Orquesta múltiples scrapers)                │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐                │
│  │ SalesysReport  │  │  GenesysReport │                │
│  │     Task       │  │      Task      │   ...          │
│  └────────────────┘  └────────────────┘                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         scrapers/base/base_scraper.py                   │
│              (Clase base - Template)                    │
│                                                          │
│   ┌──────────────────────────────────────┐             │
│   │  ejecutar() - Flujo común:           │             │
│   │  1. configurar_driver()              │             │
│   │  2. login()              ← abstracto │             │
│   │  3. navegar_a_reporte()  ← abstracto │             │
│   │  4. descargar_archivo()  ← abstracto │             │
│   │  5. procesar_datos()     ← abstracto │             │
│   │  6. guardar_en_bd()      ← opcional  │             │
│   │  7. cerrar()                          │             │
│   └──────────────────────────────────────┘             │
└────────────────────┬────────────────────────────────────┘
                     │ Herencia
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Salesys    │ │  Genesys    │ │  Navicat    │
│  Scraper    │ │  Scraper    │ │  Scraper    │
│             │ │             │ │             │
│ Implementa: │ │ Implementa: │ │ Implementa: │
│ - login()   │ │ - login()   │ │ - login()   │
│ - navegar() │ │ - navegar() │ │ - navegar() │
│ - descargar │ │ - descargar │ │ - descargar │
│ - procesar  │ │ - procesar  │ │ - procesar  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
         ┌─────────────────────────────┐
         │   core/database.py          │
         │   (Conexión centralizada)   │
         └─────────────────────────────┘
```

---

## 🔄 Flujo de Ejecución Detallado

### Escenario: Ejecutar scraper de Salesys RGA

```
1. Usuario ejecuta:
   python main.py

2. main.py crea task:
   task = SalesysReportTask("RGA")
   task.run()

3. Task crea scraper:
   scraper = SalesysScraper("RGA")
   scraper.ejecutar()  ← Usa método de BaseScraper

4. BaseScraper.ejecutar() llama en orden:

   ┌─────────────────────────────────────────┐
   │ a) configurar_driver()                  │ ← BaseScraper (concreto)
   │    └─ Abre Chrome                       │
   └─────────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────────┐
   │ b) login()                              │ ← SalesysScraper (implementa)
   │    └─ Va a URL Salesys                  │
   │    └─ Ingresa credenciales              │
   │    └─ Click en login                    │
   └─────────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────────┐
   │ c) navegar_a_reporte()                  │ ← SalesysScraper (implementa)
   │    └─ Click en "Reportes"               │
   │    └─ Selecciona "RGA"                  │
   └─────────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────────┐
   │ d) descargar_archivo()                  │ ← SalesysScraper (implementa)
   │    └─ Click en "Descargar"              │
   │    └─ Espera descarga                   │
   │    └─ Retorna: Path("downloads/RGA.xlsx") │
   └─────────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────────┐
   │ e) procesar_datos(Path)                 │ ← SalesysScraper (implementa)
   │    └─ Lee Excel con pandas              │
   │    └─ Limpia datos                      │
   │    └─ Retorna DataFrame                 │
   └─────────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────────┐
   │ f) guardar_en_bd(df)                    │ ← SalesysScraper (implementa)
   │    └─ Crea DatabaseConnection           │
   │    └─ DELETE registros viejos           │
   │    └─ INSERT nuevos datos               │
   └─────────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────────┐
   │ g) cerrar()                             │ ← BaseScraper (concreto)
   │    └─ Cierra Chrome                     │
   └─────────────────────────────────────────┘

5. Retorna DataFrame al Task
6. Task retorna resultado a main.py
7. main.py muestra resumen
```

---

## 🎨 Patrón Template Method en Acción

### BaseScraper (Esqueleto)
```python
class BaseScraper:
    def ejecutar(self):           # ← FLUJO COMÚN (no se sobreescribe)
        self.login()              # ← A implementar por subclase
        self.navegar_a_reporte()  # ← A implementar por subclase
        self.descargar_archivo()  # ← A implementar por subclase
```

### SalesysScraper (Implementación)
```python
class SalesysScraper(BaseScraper):
    # NO necesita definir ejecutar()
    # Solo implementa los detalles específicos:

    def login(self):
        # Login específico de Salesys

    def navegar_a_reporte(self):
        # Navegación específica de Salesys
```

### GenesysScraper (Otra implementación)
```python
class GenesysScraper(BaseScraper):
    # Tampoco define ejecutar()
    # Implementa sus propios detalles:

    def login(self):
        # Login específico de Genesys (diferente a Salesys)

    def navegar_a_reporte(self):
        # Navegación específica de Genesys (diferente a Salesys)
```

**Resultado:** El flujo `ejecutar()` es idéntico para todos, pero cada scraper tiene su propia lógica.

---

## 📦 Polimorfismo en Acción

```python
# Puedes tratar todos los scrapers de la misma manera:

scrapers = [
    SalesysScraper("RGA"),
    SalesysScraper("Nomina"),
    GenesysScraper("Ocupacion"),
    NavicatScraper("Validaciones")
]

# Iterar y ejecutar todos igual
for scraper in scrapers:
    df = scraper.ejecutar()  # ← Mismo método, diferentes implementaciones
    print(f"Procesados {len(df)} registros")
```

---

## 🔧 Comparación con Código Anterior

### ❌ ANTES (Sin POO - Código duplicado):
```python
# activaciones.py
def main():
    driver = webdriver.Chrome()
    driver.get("...")
    driver.find_element(...).send_keys(user)
    driver.find_element(...).send_keys(pass)
    # ... 150 líneas ...

# delivery.py
def main():
    driver = webdriver.Chrome()
    driver.get("...")
    driver.find_element(...).send_keys(user)  # ← DUPLICADO
    driver.find_element(...).send_keys(pass)  # ← DUPLICADO
    # ... 170 líneas ...

# mesa_ayuda.py
def main():
    driver = webdriver.Chrome()  # ← DUPLICADO
    driver.get("...")            # ← DUPLICADO
    # ... 122 líneas ...
```
**Problema:** Cambiar login requiere modificar 10+ archivos

---

### ✅ AHORA (Con Nivel 2 POO):
```python
# BaseScraper (define flujo UNA vez)
class BaseScraper:
    def ejecutar(self):
        self.login()
        self.descargar()
        self.procesar()

# SalesysScraper (solo lo específico)
class SalesysScraper(BaseScraper):
    def login(self):
        # Login Salesys - 10 líneas

# GenesysScraper (solo lo específico)
class GenesysScraper(BaseScraper):
    def login(self):
        # Login Genesys - 10 líneas
```
**Ventaja:** Cambiar flujo general = modificar BaseScraper (1 archivo)

---

## 🎯 Decisiones de Diseño

### ¿Por qué NO Nivel 3 (SOLID completo)?

```
Nivel 3 (RPA_ actual):
┌────────────┐
│  Factory   │ ← Complejidad innecesaria
└──────┬─────┘
       ↓
┌────────────┐
│  Registry  │ ← Complejidad innecesaria
└──────┬─────┘
       ↓
┌────────────┐
│ Abstract   │
│ Interface  │ ← Complejidad innecesaria
└──────┬─────┘
       ↓
   Scraper

Resultado: 80+ archivos para entender
```

```
Nivel 2 (rpa_new):
┌──────────────┐
│ BaseScraper  │ ← Simple y directo
└──────┬───────┘
       │ Herencia
       ↓
   SalesysScraper

Resultado: 10 archivos principales
```

---

## 📚 Conceptos Clave Visualizados

### 1. Herencia (IS-A)
```
SalesysScraper IS-A BaseScraper
GenesysScraper IS-A BaseScraper

Todos comparten:
- El flujo ejecutar()
- Métodos helper
- Configuración de driver
```

### 2. Template Method
```
BaseScraper:
┌─────────────────────┐
│ ejecutar() {        │ ← Template (esqueleto)
│   login()           │ ← Hook (a implementar)
│   navegar()         │ ← Hook (a implementar)
│   descargar()       │ ← Hook (a implementar)
│ }                   │
└─────────────────────┘
```

### 3. Composición (HAS-A)
```
BaseScraper HAS-A WebDriver
Task HAS-A Scraper
Scraper HAS-A DatabaseConnection
```

---

**Última actualización:** 2025-12-12
**Autor:** Basado en REFACTORING_PROGRESS.md
