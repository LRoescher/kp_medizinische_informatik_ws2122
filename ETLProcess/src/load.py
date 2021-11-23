import pandas as pd
import logging
import psycopg2
import numpy as np
from enum import Enum
from typing import Tuple, Optional, TypedDict, List
from psycopg2.extensions import register_adapter, AsIs

psycopg2.extensions.register_adapter(np.int64, AsIs)


class DbConfig(TypedDict):
    """
    Only for static type checking.
    """
    host: str
    port: str
    db_name: str
    username: str
    password: str
    db_schema: str


class OmopTableEnum(Enum):
    VISIT_OCCURRENCE = "visit_occurrence"
    OBSERVATION_PERIOD = "observation_period"
    PROCEDURE_OCCURRENCE = "procedure_occurrence"
    MEASUREMENT = "measurement"
    CONDITION_OCCURRENCE = "condition_occurrence"
    PERSON = "person"
    LOCATION = "location"
    PROVIDER = "provider"


class DBManager:
    """
    Class responsible for connecting to the omop-database and loading CDM-compliant tables into it.
    """

    def __init__(self, db_config: DbConfig, clear_tables: bool = False):
        """
        Creates a new Loader. Establishes a database connection.

        :param db_config:
        :param clear_tables: If set to True: clears all target omop-tables
        """
        self.DB_SCHEMA = db_config["db_schema"]
        self.conn = self._connect(db_config)
        if clear_tables:
            self.clear_omop_tables()

    def _connect(self, db_config: DbConfig) -> Optional[psycopg2._psycopg.connection]:
        """
        Connect to the PostgreSQL database server.
        :return a connection to the database server
        """
        conn = None
        try:
            # connect to the PostgreSQL server
            logging.info("Trying to connect to the database...")
            conn = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["db_name"],
                user=db_config["username"],
                password=db_config["password"])
        except (Exception, psycopg2.DatabaseError) as error:
            logging.exception("Failed to establish connection with the given parameters.")
            raise
        finally:
            return conn

    def clear_omop_tables(self) -> bool:
        """
        Removes all tables from the omop database, that have been added by this program.
        :return: True if the operation was successful
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SET search_path TO {self.DB_SCHEMA};")

            for table in OmopTableEnum:
                cursor.execute(f"Truncate {table.value} CASCADE;")
                self.conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Failed to clear omop entries from the database.")
            logging.error(error)
            self.conn.rollback()
            cursor.close()
            return False
        logging.info("Successfully cleared omop database")
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
            logging.error(f"Failed to perform query: \n Query: {query}")
            logging.error(error)
            self.conn.rollback()
            cursor.close()
            return False
        logging.info("Successfully performed query.")
        cursor.close()
        return True

    def save(self, table: OmopTableEnum, df: pd.DataFrame) -> None:
        """
        save the DataFrame in the given OMOP table

        :param table: the df should be stored
        :param df: with OMOP data
        :return:
        """
        logging.info(f"Saving Table {table.value}.")
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = f"INSERT INTO {table.value}({cols}) VALUES({','.join(['%s'] * len(df.columns))})"
        self._fire_query(query, tuples)

    def get_snomed_id(self, code, vocabulary_id: str) -> int:
        """
        Gets the Id of a SNOMED-Concept which represents the given non-standard code. The code can be for example an
        ICD-10GM or OPS code.
        :param vocabulary_id: Unique name of the vocabulary, e.g. 'ICD10GM' or 'OPS'
        :param code: the given non-standard code
        :return: the corresponding SNOMED-Id or 0 if there is no mapping for the given code
        """
        cursor = self.conn.cursor()
        cursor.execute(f"SET search_path TO {self.DB_SCHEMA}")
        try:
            # Get Omop - Concept Id of the given code
            cursor.execute(
                f"SELECT concept_id FROM concept WHERE concept_code = '{code}' AND vocabulary_id = '{vocabulary_id}';")
            concept_id_original = cursor.fetchone()[0]

            # Get Concept Id of according Snomed Concept
            cursor.execute(
                f"SELECT concept_id_2 FROM concept_relationship WHERE relationship_id = 'Maps to' AND concept_id_1 = '{concept_id_original}';")
            concept_id_snomed = int(cursor.fetchone()[0])

        except TypeError:
            # Set to 0 if no mapping was found, means 'No matching concept' in omop vocabulary
            concept_id_snomed = 0
            logging.debug(f"Could not find a mapping for {code} in {vocabulary_id}.")

        cursor.close()

        return concept_id_snomed
