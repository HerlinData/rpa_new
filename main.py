#!/usr/bin/env python3
# ====================================
# ORQUESTADOR PRINCIPAL DE RPA
# ====================================
# Este archivo ejecuta todos los scrapers de todas las plataformas
# Usa SessionManager para reutilizar sesiones y optimizar el tiempo

from scrapers.sites.salesys.core.session_manager import get_salesys_session
from scrapers.sites.salesys.reports.estado_agente_v2 import EstadoAgenteV2Scraper
from scrapers.sites.salesys.reports.rga import RGAScraper


def ejecutar_scrapers_salesys():
    """
    Ejecuta todos los scrapers de SalesYs.

    Ventaja: Un solo login para todos los scrapers (ahorro ~67% de tiempo)

    Sin SessionManager:
    - NominaScraper: login (30s) + descarga (20s) = 50s
    - RGAScraper: login (30s) + descarga (20s) = 50s
    - Total: 100s

    Con SessionManager:
    - Login compartido: 30s
    - NominaScraper: descarga (20s)
    - RGAScraper: descarga (20s)
    - Total: 70s ⚡ Ahorro: 30s (30%)
    """
    print("=" * 60)
    print("EJECUTANDO SCRAPERS DE SALESYS")
    print("=" * 60)

    # Obtener instancia singleton del SessionManager
    session = get_salesys_session()

    try:
        # ========================================
        # SCRAPER 1: ESTADO AGENTE V2
        # ========================================
        print("\n[1/2] Ejecutando scraper de Estado Agente V2...")
        estado_agente_v2 = EstadoAgenteV2Scraper(session_manager=session)
        archivo_estado_agente_v2 = estado_agente_v2.ejecutar()
        print(f"✓ Estado Agente V2 completado: {archivo_estado_agente_v2}")

        # ========================================
        # SCRAPER 2: RGA
        # ========================================
        print("\n[2/2] Ejecutando scraper de RGA...")
        rga = RGAScraper(session_manager=session)
        archivo_rga = rga.ejecutar()
        print(f"✓ RGA completado: {archivo_rga}")

        # ========================================
        # PUEDES AGREGAR MÁS SCRAPERS DE SALESYS AQUÍ
        # ========================================
        # print("\n[3/N] Ejecutando scraper de Ventas...")
        # ventas = VentasScraper(session_manager=session)
        # archivo_ventas = ventas.ejecutar()
        # print(f"✓ Ventas completado: {archivo_ventas}")

        print("\n" + "=" * 60)
        print("✓ TODOS LOS SCRAPERS DE SALESYS COMPLETADOS")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error durante ejecución de scrapers de SalesYs: {e}")
        raise

    finally:
        # IMPORTANTE: Cerrar sesión de SalesYs al finalizar TODOS los scrapers
        print("\nCerrando sesión de SalesYs...")
        session.cleanup()


def ejecutar_proceso_completo():
    """
    Ejecuta el proceso completo de RPA.

    Incluye scrapers de todas las plataformas:
    - SalesYs (Nómina, RGA, etc.)
    - SAP (próximamente)
    - Oracle (próximamente)
    - etc.
    """
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "PROCESO RPA INICIADO" + " " * 23 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        # ========================================
        # PLATAFORMA 1: SALESYS
        # ========================================
        ejecutar_scrapers_salesys()

        # ========================================
        # PLATAFORMA 2: SAP (próximamente)
        # ========================================
        # print("\n")
        # ejecutar_scrapers_sap()

        # ========================================
        # PLATAFORMA 3: ORACLE (próximamente)
        # ========================================
        # print("\n")
        # ejecutar_scrapers_oracle()

        print("\n")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 10 + "✓ PROCESO COMPLETO FINALIZADO" + " " * 18 + "║")
        print("╚" + "═" * 58 + "╝")
        print()

    except Exception as e:
        print("\n")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 12 + "✗ PROCESO FINALIZADO CON ERRORES" + " " * 14 + "║")
        print("╚" + "═" * 58 + "╝")
        print(f"\nError: {e}")
        raise


def ejecutar_solo_estado_agente_v2():
    """
    Ejemplo: Ejecutar solo el scraper de Estado Agente V2.

    Útil para pruebas o ejecuciones individuales.
    """
    print("Ejecutando solo scraper de Estado Agente V2...")

    session = get_salesys_session()
    try:
        estado_agente_v2 = EstadoAgenteV2Scraper(session_manager=session)
        archivo = estado_agente_v2.ejecutar()
        print(f"✓ Completado: {archivo}")
    finally:
        session.cleanup()


def ejecutar_solo_rga():
    """
    Ejemplo: Ejecutar solo el scraper de RGA.

    Útil para pruebas o ejecuciones individuales.
    """
    print("Ejecutando solo scraper de RGA...")

    session = get_salesys_session()
    try:
        rga = RGAScraper(session_manager=session)
        archivo = rga.ejecutar()
        print(f"✓ Completado: {archivo}")
    finally:
        session.cleanup()


# ====================================
# PUNTO DE ENTRADA
# ====================================
if __name__ == "__main__":
    import sys

    # Opciones de ejecución
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()

        if comando == "salesys":
            ejecutar_scrapers_salesys()
        elif comando == "estado_agente_v2":
            ejecutar_solo_estado_agente_v2()
        elif comando == "rga":
            ejecutar_solo_rga()
        else:
            print("Comandos disponibles:")
            print("  python main.py            - Ejecutar proceso completo")
            print("  python main.py salesys    - Solo scrapers de SalesYs")
            print("  python main.py estado_agente_v2 - Solo scraper de Estado Agente V2")
            print("  python main.py rga        - Solo scraper de RGA")
    else:
        # Por defecto: ejecutar proceso completo
        ejecutar_proceso_completo()
