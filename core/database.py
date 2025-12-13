# ====================================
# PASO 2: CONEXIÓN A BASE DE DATOS
# ====================================
# Clase centralizada para manejar conexiones a SQL Server
# Evita duplicar código de conexión en cada script

from sqlalchemy import create_engine
import pandas as pd
from typing import Optional


class DatabaseConnection:
    """
    Maneja conexiones a SQL Server de forma centralizada.

    Uso:
        db = DatabaseConnection(server, database)
        df = db.query("SELECT * FROM tabla")
        db.insert_dataframe(df, "nombre_tabla")
    """

    def __init__(self, server: str, database: str, user: str = None, password: str = None):
        """
        TODO: Implementar inicialización de conexión

        Args:
            server: Nombre del servidor SQL
            database: Nombre de la base de datos
            user: Usuario (opcional, si usa autenticación Windows déjalo en None)
            password: Contraseña (opcional)
        """
        pass

    def connect(self):
        """
        TODO: Crear conexión usando SQLAlchemy

        Ejemplo:
            connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
            self.engine = create_engine(connection_string)
        """
        pass

    def query(self, sql: str) -> pd.DataFrame:
        """
        TODO: Ejecutar consulta SELECT y retornar DataFrame

        Args:
            sql: Query SQL

        Returns:
            DataFrame con resultados
        """
        pass

    def execute(self, sql: str):
        """
        TODO: Ejecutar comando SQL (INSERT, UPDATE, DELETE)

        Args:
            sql: Comando SQL
        """
        pass

    def insert_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """
        TODO: Insertar DataFrame en tabla

        Args:
            df: DataFrame a insertar
            table_name: Nombre de la tabla
            if_exists: 'append', 'replace', o 'fail'
        """
        pass

    def delete_and_insert(self, df: pd.DataFrame, table_name: str, condition: str):
        """
        TODO: Borrar registros según condición y luego insertar

        Patrón común: DELETE WHERE mes = X AND year = Y, luego INSERT

        Args:
            df: DataFrame a insertar
            table_name: Nombre de la tabla
            condition: Condición WHERE para el DELETE
        """
        pass

    def close(self):
        """
        TODO: Cerrar conexión
        """
        pass
