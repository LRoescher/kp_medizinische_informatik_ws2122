from random import randrange

import pandas as pd
import logging
import psycopg2
import numpy as np
from enum import Enum
from typing import Tuple, Optional, List
from psycopg2.extensions import register_adapter, AsIs
from Backend.common.config import generate_config, DbConfig

psycopg2.extensions.register_adapter(np.int64, AsIs)


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
            logging.info("Successfully connected to the database.")
        except (Exception, psycopg2.DatabaseError) as error:
            logging.exception("Failed to establish connection with the given parameters.")
            raise
        finally:
            return conn

    def check_if_table_is_empty(self, table_name: str):
        """
        Checks if the database is empty.
        :return: True if the database is empty, else false
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SET search_path TO {self.DB_SCHEMA};")

            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            result = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return 0 == result

        except (Exception, psycopg2.DatabaseError) as error:
            logging.warning("Failed to check database. Returning 0.")
            logging.warning(error)
            self.conn.rollback()
            cursor.close()
            return False

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
        logging.info("Successfully cleared omop database.")
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

    def get_snomed_id(self, code: str, vocabulary_id: str) -> int:
        """
        Gets the Id of a SNOMED-Concept which represents the given non-standard code. The code can be for example an
        ICD-10GM or OPS code.
        :param vocabulary_id: Unique name of the vocabulary, e.g. 'ICD10GM' or 'OPS'
        :param code: the given non-standard code
        :return: the corresponding SNOMED-Id or 0 if there is no mapping for the given code
        """
        # Remove trailing !/+ characters, because they are not included in OMOP concepts
        code = code.rstrip("!+")

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

    def send_query(self, query: str) -> pd.DataFrame:
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = None
        try:
            result = pd.read_sql_query(query, self.conn)

        except TypeError:
            logging.debug(f"Error executing query: {query}")

        cursor.close()
        return result

    def generate_condition_occurrence_id(self) -> int:
        """
        Generates a unique identifier that is not already taken by an entry in the condition_occurrence table.
        """
        new_id = randrange(10000, 9999999)
        while self._id_is_taken(OmopTableEnum.CONDITION_OCCURRENCE.value, "condition_occurrence_id", new_id):
            new_id = randrange(10000, 9999999)
        return new_id

    def generate_patient_id(self) -> int:
        """
        Generates a unique identifier that is not already taken by an entry in the person/patient table.
        """
        new_id = randrange(10000, 9999999)
        while self._id_is_taken(OmopTableEnum.PERSON.value, "person_id", new_id):
            new_id = randrange(10000, 9999999)
        return new_id

    def _id_is_taken(self, table: str, field: str, new_id: int):
        """
        Checks if the given id is taken by an entry for the given field of the given table.
        """
        query: str = f"SELECT * FROM {self.DB_SCHEMA}.{table} WHERE {field} = {new_id}"
        result_df: pd.DataFrame = self.send_query(query)
        return not result_df.empty


if __name__ == "__main__":
    db_config = generate_config()
    db_manager = DBManager(db_config=db_config, clear_tables=False)
    print(db_manager.get_snomed_id('M30.3', 'ICD10GM'))
    print(db_manager.check_if_table_is_empty())
