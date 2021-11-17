import pandas as pd
import psycopg2
import numpy as np
from enum import Enum
from typing import Tuple, Optional, TypedDict, List
from psycopg2.extensions import register_adapter, AsIs
psycopg2.extensions.register_adapter(np.int64, AsIs)


class DB_CONFIG(TypedDict):
    '''
     only for static type checking
    '''
    host: str
    port: str
    db_name: str
    username: str
    password: str
    db_schema: str


class OMOP_TABLE(Enum):
    PERSON = "person"
    LOCATION = "location"
    OBSERVATION_PERIOD = "observation_period"
    PROVIDER = "provider"


class Loader:
    """
    Class responsible for connecting to the omop-database and loading CDM-compliant tables into it.
    """

    def __init__(self, db_config: DB_CONFIG, clear_tables: bool = False):
        """
        Creates a new Loader. Establishes a database connection.

        :param db_config:
        :param clear_tables: If set to True: clears all target omop-tables
        """
        self.DB_SCHEMA = db_config["db_schema"]
        self.conn = self._connect(db_config)
        if clear_tables:
            self.clear_omop_tables()

    def _connect(self, db_config: DB_CONFIG) -> Optional[psycopg2._psycopg.connection]:
        """
        Connect to the PostgreSQL database server.
        :return a connection to the database server
        """
        conn = None
        try:
            # connect to the PostgreSQL server
            print('[INFO] Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["db_name"],
                user=db_config["username"],
                password=db_config["password"])
            print('[INFO] Successfully connected to the PostgreSQL database.')
        except Exception as error:
            print(f"[ERROR] Failed to establish connection: \n {error}")
        finally:
            return conn

    def clear_omop_tables(self) -> bool:
        """
        Removes all tables from the omop database, that have been added by this program.
        :return: True if the operation was successful
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SET search_path TO {self.DB_SCHEMA}")

            for table in OMOP_TABLE:
                cursor.execute(f"DELETE FROM {table.value}")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"[ERROR] Failed to clear omop entries from the database \n Message: {error}")
            self.conn.rollback()
            cursor.close()
            return False
        print("[INFO] Successfully cleared omop database")
        cursor.close()
        return True

    def _fire_query(self, query: str, tuples: List[Tuple]) -> bool:
        """
        Sends the query enriched with dataframe entries to the connected database server.

        :param query: the query itself with placeholders
        :param tuples: the data which will be inserted into the query
        :return: True if the query was successfully carried out
        """
        cursor = self.conn.cursor()
        try:
            # Select database schema and execute query on it
            cursor.execute(f"SET search_path TO {self.DB_SCHEMA}")
            cursor.executemany(query, tuples)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"[ERROR] Failed to perform query: \n Query: {query} \n Message: {error}")
            self.conn.rollback()
            cursor.close()
            return False
        print("[INFO] Successfully performed query.")
        cursor.close()
        return True

    def save(self, table: OMOP_TABLE, df: pd.DataFrame):
        '''
        save the DataFrame in the given OMOP table

        :param table: the df should be stored
        :param df: with OMOP data
        :return:
        '''
        print(f"[INFO] Saving Table {table.value}.")
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = f"INSERT INTO {table.value}({cols}) VALUES({','.join(['%s']*len(df.columns))})"
        self._fire_query(query, tuples)
