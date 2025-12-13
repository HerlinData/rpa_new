# ====================================
# PASO 5: TAREAS (OPCIONAL)
# ====================================
# Si quieres orquestar múltiples scrapers, puedes usar Tasks
# Una Task encapsula la ejecución de un scraper + lógica adicional

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTask(ABC):
    """
    Clase base para tareas que pueden ejecutar uno o más scrapers.

    Útil si necesitas:
    - Ejecutar múltiples scrapers en secuencia
    - Combinar datos de varias fuentes
    - Agregar lógica pre/post ejecución
    """

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.result = None

    def run(self) -> Dict[str, Any]:
        """
        Ejecuta la tarea completa.

        Returns:
            Diccionario con resultados
        """
        try:
            print(f"\n{'='*50}")
            print(f"Ejecutando tarea: {self.task_name}")
            print(f"{'='*50}\n")

            self.result = self.execute()

            print(f"\n✓ Tarea '{self.task_name}' completada exitosamente")
            return self.result

        except Exception as e:
            print(f"\n✗ Error en tarea '{self.task_name}': {str(e)}")
            raise

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        TODO EN SUBCLASE: Implementar lógica de ejecución

        Returns:
            Diccionario con resultados de la tarea
        """
        pass


# ====================================
# EJEMPLO DE TAREA CONCRETA
# ====================================
class SalesysReportTask(BaseTask):
    """
    Tarea que ejecuta un scraper de Salesys y retorna el resultado.
    """

    def __init__(self, reporte_nombre: str):
        super().__init__(task_name=f"Salesys-{reporte_nombre}")
        self.reporte_nombre = reporte_nombre

    def execute(self) -> Dict[str, Any]:
        """
        TODO: Implementar ejecución de scraper

        Ejemplo:
            from scrapers.implementaciones.salesys_scraper import SalesysScraper

            scraper = SalesysScraper(self.reporte_nombre)
            df = scraper.ejecutar()

            return {
                'status': 'success',
                'reporte': self.reporte_nombre,
                'registros': len(df),
                'data': df
            }
        """
        print(f"TODO: Ejecutar scraper {self.reporte_nombre}")
        return {
            'status': 'pending',
            'reporte': self.reporte_nombre
        }
