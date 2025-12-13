#!/usr/bin/env python3
# ====================================
# TEST: SeleniumConfig
# ====================================
# Script para probar la configuración de Selenium
# Ejecutar: python test_selenium_config.py

from utils.selenium_config import SeleniumConfig
import time
import warnings
import logging
import os
import sys
from contextlib import contextmanager

# Silenciar warnings y logs
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.CRITICAL)
os.environ['PYTHONWARNINGS'] = 'ignore'


@contextmanager
def suppress_stderr():
    """Contexto para suprimir mensajes de stderr (errores de Chrome, DevTools, etc.)"""
    original_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr


def test_default_config():
    """Prueba configuración por defecto"""
    print("=" * 60)
    print("TEST 1: Configuración por defecto")
    print("=" * 60)

    with suppress_stderr():
        driver = SeleniumConfig.create_default()

        # Navegar a Google
        driver.get("https://www.google.com")
        title = driver.title
        url = driver.current_url

        time.sleep(2)
        driver.quit()

    print(f"✓ Título de página: {title}")
    print(f"✓ URL actual: {url}")
    print("✓ Test completado\n")


def test_headless_mode():
    """Prueba modo headless (sin interfaz gráfica)"""
    print("=" * 60)
    print("TEST 2: Modo Headless")
    print("=" * 60)

    with suppress_stderr():
        config = SeleniumConfig(headless=True)
        driver = config.create_driver()

        driver.get("https://www.python.org")
        title = driver.title

        driver.quit()

    print(f"✓ Título de página: {title}")
    print(f"✓ Modo headless funcionando")
    print("✓ Test completado\n")


def test_custom_download_dir():
    """Prueba directorio de descargas personalizado"""
    print("=" * 60)
    print("TEST 3: Directorio de descargas personalizado")
    print("=" * 60)

    from pathlib import Path
    custom_dir = Path("./temp_downloads_test")

    with suppress_stderr():
        config = SeleniumConfig(download_dir=str(custom_dir))
        driver = config.create_driver()
        download_path = config.download_dir
        dir_exists = custom_dir.exists()
        driver.quit()

    print(f"✓ Directorio de descargas: {download_path}")
    print(f"✓ Directorio existe: {dir_exists}")

    # Limpiar directorio de prueba
    if custom_dir.exists():
        custom_dir.rmdir()
        print("✓ Directorio de prueba eliminado")

    print("✓ Test completado\n")


def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "PRUEBAS DE SELENIUM CONFIG" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    tests = [
        ("Configuración por defecto", test_default_config),
        ("Modo headless", test_headless_mode),
        ("Directorio personalizado", test_custom_download_dir),
    ]

    for i, (name, test_func) in enumerate(tests, 1):
        try:
            test_func()
        except Exception as e:
            print(f"✗ Error en test '{name}': {str(e)}\n")

    print("=" * 60)
    print("RESUMEN: Todas las pruebas completadas")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n✗ Error general: {str(e)}")
