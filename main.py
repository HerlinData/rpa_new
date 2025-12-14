#!/usr/bin/env python3
# ====================================
# ORQUESTADOR PRINCIPAL DE RPA
# ====================================
# Este archivo ejecuta todos los scrapers de todas las plataformas
# Usa SessionManager para reutilizar sesiones y optimizar el tiempo

from scrapers.sites.salesys.core.session_manager import get_salesys_session
from scrapers.sites.salesys.reports.estado_agente_v2 import EstadoAgenteV2Scraper
from scrapers.sites.salesys.reports.rga import RGAScraper
from scrapers.sites.salesys.reports.delivery_rechazo import DeliveryRechazoScraper

def ejecutar_scrapers_salesys():
    """
    Ejecuta todos los scrapers de SalesYs para un rango de fechas.
    """
    print("=" * 60)
    print("EJECUTANDO SCRAPERS DE SALESYS")
    print("=" * 60)

    # --- Definir el rango de fechas a procesar ---
    # Ejemplo: procesar los últimos 2 días
    from datetime import date, timedelta
    hoy = date.today()
    fechas_a_procesar = [(hoy - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(2)]
    print(f"Rango de fechas a procesar: {fechas_a_procesar}")
    # -----------------------------------------

    # Obtener instancia singleton del SessionManager
    session = get_salesys_session()

    try:
        # ========================================
        # SCRAPER 1: ESTADO AGENTE V2
        # ========================================
        print("\n[1/2] Iniciando scraper de Estado Agente V2...")
        estado_agente_v2 = EstadoAgenteV2Scraper(session_manager=session)
        estado_agente_v2.ejecutar(fechas=fechas_a_procesar)
        print("✓ Proceso de Estado Agente V2 finalizado.")

        # ========================================
        # SCRAPER 2: RGA
        # ========================================)
        productos_default = ["DELIVERY", "HFC"]
        rga = RGAScraper(session_manager=session, productos=productos_default)
        rga.ejecutar(fechas=fechas_a_procesar)
        print("✓ Proceso de RGA finalizado.")
           
        
        
        
        
        
        # ========================================
        # SCRAPER 3: DELIVERY RECHAZO
        # ========================================)
        rga = DeliveryRechazoScraper(session_manager=session)
        rga.ejecutar(fechas=fechas_a_procesar)
        print("✓ Proceso de DELIVERY RECHAZO finalizado.")
        
        print("\n" + "=" * 60)
        print("✓ TODOS LOS SCRAPERS DE SALESYS COMPLETADOS")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error durante ejecución de scrapers de SalesYs: {e}")
        # No relanzar la excepción para permitir que el cleanup se ejecute
        # raise

    finally:
        # IMPORTANTE: Cerrar sesión de SalesYs al finalizar TODOS los scrapers
        print("\nCerrando sesión de SalesYs...")
        session.cleanup()


def ejecutar_proceso_completo():
    """
    Ejecuta el proceso completo de RPA.
    """
    try:
        # ========================================
        # PLATAFORMA 1: SALESYS
        # ========================================
        ejecutar_scrapers_salesys()

    except Exception as e:
        print("\n")
        print("║" + " " * 12 + "✗ PROCESO FINALIZADO CON ERRORES" + " " * 14 + "║")
        print(f"\nError: {e}")
        # raise


def ejecutar_solo_estado_agente_v2():
    """
    Ejecuta solo el scraper de Estado Agente V2 para un rango de fechas.
    """
    print("Ejecutando solo scraper de Estado Agente V2...")
    from datetime import date, timedelta
    hoy = date.today()
    fechas_a_procesar = [(hoy - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(2)]
    print(f"Rango de fechas a procesar: {fechas_a_procesar}")
    
    estado_agente_v2 = EstadoAgenteV2Scraper()
    estado_agente_v2.ejecutar(fechas=fechas_a_procesar)
    print("✓ Proceso de Estado Agente V2 finalizado.")


def ejecutar_solo_rga():
    """
    Ejecuta solo el scraper de RGA para un rango de fechas.
    """
    print("Ejecutando solo scraper de RGA...")
    from datetime import date, timedelta
    hoy = date.today()
    fechas_a_procesar = [(hoy - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(2)]
    print(f"Rango de fechas a procesar: {fechas_a_procesar}")

    # Default temporal para CLI - La web pasará productos dinámicamente
    productos_default = ["DELIVERY", "HFC"]
    print(f"Productos a descargar: {productos_default}")

    rga = RGAScraper(productos=productos_default)
    rga.ejecutar(fechas=fechas_a_procesar)
    print("✓ Proceso de RGA finalizado.")
    
def ejecutar_solo_DeliveryRechazo():
    """
    Ejecuta solo el scraper de DeliveryRechazo para un rango de fechas.
    """
    print("Ejecutando solo scraper de DeliveryRechazo...")
    from datetime import date, timedelta
    hoy = date.today()
    fechas_a_procesar = [(hoy - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(2)]
    print(f"Rango de fechas a procesar: {fechas_a_procesar}")

    # Default temporal para CLI - La web pasará usuarios dinámicamente
    usuarios_default = ["Todo"]
    print(f"Usuarios a descargar: {usuarios_default}")

    delivery_rechazo = DeliveryRechazoScraper(usuarios=usuarios_default)
    delivery_rechazo.ejecutar(fechas=fechas_a_procesar)
    print("✓ Proceso de DeliveryRechazo finalizado.")


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
        elif comando == "deliveryrechazo":
            ejecutar_solo_DeliveryRechazo()
        else:
            print("Comandos disponibles:")
            print("  python main.py            - Ejecutar proceso completo")
            print("  python main.py salesys    - Solo scrapers de SalesYs")
            print("  python main.py estado_agente_v2 - Solo scraper de Estado Agente V2")
            print("  python main.py rga        - Solo scraper de RGA")
    else:
        # Por defecto: ejecutar proceso completo
        ejecutar_proceso_completo()
