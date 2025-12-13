# ====================================
# PASO 7: PUNTO DE ENTRADA PRINCIPAL
# ====================================
# Este es el archivo principal que ejecuta todas las tareas

from tasks.task_interface import SalesysReportTask


def main():
    """
    TODO: Implementar ejecución de tareas

    Ejemplo de flujo:
    1. Ejecutar scraper de Salesys RGA
    2. Ejecutar scraper de Salesys Nómina
    3. Ejecutar scraper de Genesys (cuando lo crees)
    4. Mostrar resumen de resultados
    """

    print("=" * 60)
    print(" RPA - Sistema de Automatización de Reportes")
    print("=" * 60)

    # TODO: Descomentar cuando implementes las tareas
    # task_rga = SalesysReportTask("RGA")
    # resultado_rga = task_rga.run()

    # task_nomina = SalesysReportTask("Nomina")
    # resultado_nomina = task_nomina.run()

    print("\nTODO: Implementar ejecución de tareas")


if __name__ == "__main__":
    main()
