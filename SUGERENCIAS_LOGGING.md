# Sugerencias de Implementación de Logging

## Estado Actual

El proyecto usa `print()` en 6 archivos principales:
- `main.py` - Progreso general de ejecución
- `base_salesys.py` - Detalles de procesamiento por item
- `session_manager.py` - Estado de login
- `route_builder.py` - Advertencias de configuración
- `settings.py` - Advertencias de carga
- `base_scraper.py` - Estado del navegador

Variables de logging ya configuradas en `config/settings.py`:
```python
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## Opción 1: Redirección Externa (Task Scheduler) ⭐ RECOMENDADA

### Riesgo: 0% | Tiempo: 2 minutos

### Descripción
Guardar los logs mediante redirección de salida en Windows Task Scheduler, **SIN modificar ningún archivo Python**.

### Implementación

#### En Task Scheduler:

**Antes:**
```batch
python C:\ti\rpa_new\main.py
```

**Después:**
```batch
python C:\ti\rpa_new\main.py >> C:\ti\rpa_new\logs\rpa_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1
```

#### Crear directorio de logs (una sola vez):
```batch
mkdir C:\ti\rpa_new\logs
```

### Ventajas
- ✅ **CERO cambios en código Python**
- ✅ **Imposible romper funcionalidad existente**
- ✅ Todos los `print()` se guardan automáticamente
- ✅ Errores también se capturan (stderr)
- ✅ Funciona con CUALQUIER print futuro
- ✅ Fácil de desactivar (remover `>> ...`)

### Desventajas
- ⚠️ Sin timestamps en cada línea individual
- ⚠️ Sin niveles (INFO/ERROR/WARNING)
- ⚠️ Sin rotación automática de archivos
- ⚠️ Todos los logs en un solo archivo por día

### Ejemplo de salida

**Archivo:** `logs/rpa_20251214.log`
```
==========================================================
EJECUTANDO SCRAPERS DE SALESYS
==========================================================
Rango de fechas a procesar: [datetime.date(2025, 12, 14)]

[1/2] Iniciando scraper de Estado Agente V2...
[SalesYs] Reutilizando sesión activa

[2025-12-14 - Todo]
  ✓ EstadoAgente14.csv
✓ Proceso de Estado Agente V2 finalizado.
```

### Limpieza de logs antiguos (opcional)

Crear script `limpiar_logs.bat`:
```batch
@echo off
REM Eliminar logs de más de 7 días
forfiles /p "C:\ti\rpa_new\logs" /s /m *.log /d -7 /c "cmd /c del @path"
```

Ejecutar este script en Task Scheduler cada semana.

---

## Opción 2: Script Wrapper con Timestamps ⭐⭐

### Riesgo: 5% | Tiempo: 10 minutos

### Descripción
Crear un script `.bat` que ejecute el RPA y agregue timestamps de inicio/fin, **SIN modificar archivos Python**.

### Implementación

#### Crear `run_rpa.bat`:
```batch
@echo off
REM ====================================
REM Wrapper para ejecutar RPA con logs
REM ====================================

set PROJECT_DIR=C:\ti\rpa_new
set LOG_DIR=%PROJECT_DIR%\logs
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\rpa_%TIMESTAMP%.log

REM Crear directorio si no existe
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Cabecera del log
echo ========================================== > "%LOG_FILE%"
echo RPA AUTOMATION - INICIO >> "%LOG_FILE%"
echo Fecha: %date% >> "%LOG_FILE%"
echo Hora: %time% >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Ejecutar RPA y capturar salida
cd /d "%PROJECT_DIR%"
python main.py >> "%LOG_FILE%" 2>&1

REM Pie del log
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo RPA AUTOMATION - FIN >> "%LOG_FILE%"
echo Fecha: %date% >> "%LOG_FILE%"
echo Hora: %time% >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"

REM Si hubo error, crear archivo de alerta
if %ERRORLEVEL% NEQ 0 (
    echo ERROR >> "%LOG_DIR%\ALERTA_ERROR.txt"
    echo Revisar: %LOG_FILE% >> "%LOG_DIR%\ALERTA_ERROR.txt"
)
```

#### Modificar Task Scheduler:
```batch
# En lugar de ejecutar: python main.py
# Ejecutar: C:\ti\rpa_new\run_rpa.bat
```

### Ventajas
- ✅ **CERO cambios en código Python**
- ✅ Timestamps de inicio/fin automáticos
- ✅ Logs organizados por fecha y hora
- ✅ Archivo de alerta si hubo error
- ✅ Fácil de personalizar
- ✅ Fácil de desactivar (ejecutar main.py directamente)

### Desventajas
- ⚠️ Sin timestamps en cada línea individual
- ⚠️ Requiere mantener archivo .bat adicional
- ⚠️ Específico de Windows

### Ejemplo de salida

**Archivo:** `logs/rpa_20251214_093000.log`
```
==========================================
RPA AUTOMATION - INICIO
Fecha: 14/12/2025
Hora: 09:30:00.45
==========================================

==========================================================
EJECUTANDO SCRAPERS DE SALESYS
==========================================================
[...]

==========================================
RPA AUTOMATION - FIN
Fecha: 14/12/2025
Hora: 09:45:23.12
==========================================
```

### Variante con argumentos

Para ejecutar scrapers específicos desde el wrapper:

```batch
REM run_rpa.bat con parámetros
python main.py %* >> "%LOG_FILE%" 2>&1
```

Uso:
```batch
run_rpa.bat rga          # Solo scraper RGA
run_rpa.bat estado_agente_v2  # Solo Estado Agente
```

---

## Opción 3: Interceptor de Prints (PrintLogger) ⭐⭐⭐

### Riesgo: 20-30% | Tiempo: 30 minutos

### Descripción
Interceptar automáticamente todos los `print()` y guardarlos con timestamps, modificando **SOLO main.py** (1 archivo, 2 líneas).

### Implementación

#### Paso 1: Crear `utils/print_logger.py`

```python
# utils/print_logger.py
import sys
from datetime import datetime
from pathlib import Path

class PrintLogger:
    """
    Captura automáticamente todos los print() y los guarda en archivo.
    NO requiere modificar código existente de scrapers.
    """
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log_file = open(log_file, 'a', encoding='utf-8')

    def write(self, message):
        # Escribir a consola (comportamiento normal)
        self.terminal.write(message)

        # Escribir a archivo con timestamp
        if message.strip():  # Solo si no es línea vacía
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_file.write(f"[{timestamp}] {message}")
        else:
            self.log_file.write(message)

        self.log_file.flush()  # Guardar inmediatamente

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        if self.log_file:
            self.log_file.close()


def setup_print_logging(log_dir="logs", keep_days=7):
    """
    Activa el logging automático de prints.
    Llama esto UNA VEZ al inicio de main.py

    Args:
        log_dir: Directorio donde guardar logs
        keep_days: Días de logs a mantener (elimina más antiguos)

    Returns:
        Path del archivo de log creado
    """
    # Crear directorio de logs
    base_dir = Path(__file__).parent.parent
    log_path = base_dir / log_dir
    log_path.mkdir(exist_ok=True)

    # Nombre de archivo con fecha y hora
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_path / f"rpa_{timestamp}.log"

    # Redirigir stdout y stderr
    logger = PrintLogger(log_file)
    sys.stdout = logger
    sys.stderr = logger

    # Limpieza de logs antiguos
    cleanup_old_logs(log_path, keep_days)

    print(f"{'='*60}")
    print(f"RPA AUTOMATION - Inicio de ejecución")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log guardado en: {log_file}")
    print(f"{'='*60}\n")

    return log_file


def cleanup_old_logs(log_path, keep_days):
    """Elimina logs más antiguos que keep_days"""
    import time
    cutoff_time = time.time() - (keep_days * 86400)

    deleted_count = 0
    for old_log in log_path.glob("rpa_*.log"):
        if old_log.stat().st_mtime < cutoff_time:
            try:
                old_log.unlink()
                deleted_count += 1
            except Exception:
                pass

    if deleted_count > 0:
        print(f"[INFO] Logs antiguos eliminados: {deleted_count}")
```

#### Paso 2: Modificar `main.py` (SOLO 2 líneas)

```python
# main.py
# AGREGAR AL INICIO, después de los imports
from utils.print_logger import setup_print_logging

def main():
    # AGREGAR ESTA LÍNEA como primera instrucción
    setup_print_logging(keep_days=7)

    # ... resto del código sin cambios
```

### Ventajas
- ✅ Timestamps automáticos en CADA línea
- ✅ Solo modifica 1 archivo (main.py, 2 líneas)
- ✅ Todos los scrapers quedan sin tocar
- ✅ Limpieza automática de logs antiguos
- ✅ Funciona en consola Y en Task Scheduler
- ✅ Fácil de desactivar (comentar 1 línea)

### Desventajas
- ⚠️ Modifica `sys.stdout` (podría afectar librerías que usan stdout directamente)
- ⚠️ Prints con caracteres especiales podrían romper encoding
- ⚠️ Requiere probar que no rompa nada
- ⚠️ Si falla, hay que debuggear

### Ejemplo de salida

**Archivo:** `logs/rpa_20251214_093000.log`
```
[2025-12-14 09:30:00] ============================================================
[2025-12-14 09:30:00] RPA AUTOMATION - Inicio de ejecución
[2025-12-14 09:30:00] Timestamp: 2025-12-14 09:30:00
[2025-12-14 09:30:00] Log guardado en: /mnt/c/ti/rpa_new/logs/rpa_20251214_093000.log
[2025-12-14 09:30:00] ============================================================
[2025-12-14 09:30:00]
[2025-12-14 09:30:00] ==========================================================
[2025-12-14 09:30:00] EJECUTANDO SCRAPERS DE SALESYS
[2025-12-14 09:30:00] ==========================================================
[2025-12-14 09:30:01] Rango de fechas a procesar: [datetime.date(2025, 12, 14)]
[2025-12-14 09:30:01]
[2025-12-14 09:30:01] [1/2] Iniciando scraper de Estado Agente V2...
[2025-12-14 09:30:02] [SalesYs] Reutilizando sesión activa
[2025-12-14 09:30:03]
[2025-12-14 09:30:03] [2025-12-14 - Todo]
[2025-12-14 09:30:15]   ✓ EstadoAgente14.csv
[2025-12-14 09:30:15] ✓ Proceso de Estado Agente V2 finalizado.
```

### Variante: Logs separados por nivel

Si quieres logs de errores separados, modifica `print_logger.py`:

```python
class PrintLogger:
    def __init__(self, log_file, error_file=None):
        self.terminal = sys.stdout
        self.log_file = open(log_file, 'a', encoding='utf-8')
        self.error_file = open(error_file, 'a', encoding='utf-8') if error_file else None

    def write(self, message):
        # ... código anterior ...

        # Si es error, guardar también en archivo de errores
        if self.error_file and any(x in message for x in ['✗', 'ERROR', 'Exception', 'Traceback']):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.error_file.write(f"[{timestamp}] {message}")
            self.error_file.flush()
```

### Plan de Rollback

Si algo falla después de implementar:

```python
# main.py
# COMENTAR ESTA LÍNEA:
# setup_print_logging(keep_days=7)

# Todo vuelve a funcionar como antes
```

---

## Comparación de Opciones

| Característica | Opción 1 | Opción 2 | Opción 3 |
|----------------|----------|----------|----------|
| **Riesgo** | 0% | 5% | 20-30% |
| **Tiempo implementación** | 2 min | 10 min | 30 min |
| **Archivos Python modificados** | 0 | 0 | 1 (main.py) |
| **Timestamps por línea** | ❌ | ❌ | ✅ |
| **Timestamps inicio/fin** | ❌ | ✅ | ✅ |
| **Limpieza automática** | ❌ | ⚠️ Manual | ✅ |
| **Logs históricos** | ✅ | ✅ | ✅ |
| **Funciona en consola** | ✅ | ✅ | ✅ |
| **Funciona automatizado** | ✅ | ✅ | ✅ |
| **Fácil de revertir** | ✅ | ✅ | ✅ |
| **Portabilidad (Linux/Mac)** | ⚠️ | ❌ | ✅ |

---

## Recomendación por Escenario

### Escenario 1: "Solo necesito saber si corrió y si hubo errores"
→ **Opción 1** (Redirección Task Scheduler)

### Escenario 2: "Necesito timestamps de cuándo inició y terminó"
→ **Opción 2** (Script Wrapper)

### Escenario 3: "Necesito timestamp de cada operación para debugging"
→ **Opción 3** (PrintLogger)

### Escenario 4: "No quiero tocar NADA de código Python"
→ **Opción 1 o 2**

### Escenario 5: "Quiero lo más completo pero con poco riesgo"
→ **Empezar con Opción 1**, luego migrar a **Opción 3** cuando tengas tiempo de probar

---

## Plan de Implementación Sugerido

### Fase 1: AHORA (2 minutos)
1. Implementar **Opción 1** (Redirección Task Scheduler)
2. Dejar correr 1 semana
3. Verificar que los logs sean útiles

### Fase 2: Próxima semana (10 minutos)
1. Si necesitas timestamps de inicio/fin, implementar **Opción 2** (Wrapper)
2. Reemplazar Opción 1 con Opción 2 en Task Scheduler

### Fase 3: Cuando hagas la web (30 minutos)
1. La web capturará la salida con `subprocess`
2. Si necesitas timestamps detallados, implementar **Opción 3**
3. Probar bien antes de usar en producción

---

## Notas Finales

### Sobre la integración con la web

Todas estas opciones son compatibles con la arquitectura web planteada:

```python
# web_app.py
import subprocess

@app.route('/ejecutar', methods=['POST'])
def ejecutar_scraper():
    scraper = request.form.get('scraper')

    # Ejecutar y capturar salida (funciona con las 3 opciones)
    proceso = subprocess.run(
        ['python', 'main.py', scraper],
        capture_output=True,
        text=True
    )

    # Los logs TAMBIÉN se guardan en archivo (gracias a las opciones 1, 2 o 3)
    return f"<pre>{proceso.stdout}</pre>"
```

### Sobre Base de Datos

Ninguna de estas opciones usa base de datos porque:
- Los scrapers actuales funcionan sin DB
- Agregar DB sería una modificación mayor
- Los archivos de texto son suficientes para el caso de uso actual

Cuando realmente necesites DB (para análisis histórico, dashboards, etc.), ese será otro proyecto de refactoring.

### Contacto y Soporte

Si implementas alguna de estas opciones y tienes problemas:
1. Revisa que el directorio `logs/` exista
2. Verifica permisos de escritura
3. Revisa encoding (debe ser UTF-8)
4. Si falla, revierte los cambios (comentar líneas agregadas)

---

**Fecha de creación:** 2025-12-14
**Versión del proyecto:** Refactorización "Refact claude" (commit 4bbfbf0)
