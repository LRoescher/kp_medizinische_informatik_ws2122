import pandas as pd
import logging
import psycopg2
import numpy as np
from random import randrange
from typing import Tuple, Optional, List
from psycopg2.extensions import register_adapter, AsIs
from Backend.common.config import generate_config, DbConfig
from Backend.common.omop_enums import OmopTableEnum, OmopConditionOccurrenceFieldsEnum, OmopPersonFieldsEnum, \
    SnomedConcepts

psycopg2.extensions.register_adapter(np.int64, AsIs)


class DBManager:
    """
    Class responsible for connecting to and interacting with the omop-database.
    """

    # Provider-Id that is used for tables generated using the frontend
    PROVIDER_ID: int = 999999

    def __init__(self, db_config: DbConfig, clear_tables: bool = False):
        """
        Creates a new DatabaseManager. Establishes a new database connection with the parameters specified in the given
        DbConfig.

        :param db_config: The configuration (Url, username, password, ...) for the database
        :param clear_tables: If set to True: clears all target omop-tables
        """
        self.DB_SCHEMA = db_config["db_schema"]
        self.conn = self._connect(db_config)
        if clear_tables:
            self.clear_omop_tables()

    def _connect(self, db_config: DbConfig) -> Optional[psycopg2._psycopg.connection]:
        """
        Connect to the PostgreSQL database server.
        :return: a connection to the database server or None if connecting failed
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
        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.exception("Failed to establish connection with the given parameters.")
            logging.exception(error)
        finally:
            return conn

    def check_if_table_is_empty(self, table_name: str) -> bool:
        """
        Checks if the given table is empty. If there is no active connection this will raise an AttributeError

        :return: True if the table is empty, False if the table is not empty
        :raises AttributeError: If the operation fails, e.g. if there is no active database connection
        """
        cursor = None

        try:
            cursor = self.conn.cursor()
            query: str = f"SELECT COUNT(*) FROM {self.DB_SCHEMA}.{table_name};"
            cursor.execute(query)
            result = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return 0 == result

        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            try:
                self.conn.rollback()
                cursor.close()
            except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error2:
                logging.error("Another error occurred during shutdown. There might be data loss.")
                logging.error(error2)
            raise AttributeError("Error during database operation. Check if there is an active connection.")

    def clear_omop_tables(self) -> bool:
        """
        Removes all tables from the omop database, that have been added by this program.

        :return: True if the operation was successful
        :raises AttributeError: If the operation fails, e.g. if there is no active database connection
        """
        cursor = None

        try:
            cursor = self.conn.cursor()
            for table in OmopTableEnum:
                query: str = f"Truncate {self.DB_SCHEMA}.{table.value} CASCADE;"
                cursor.execute(query)
                self.conn.commit()
            logging.info("Successfully cleared omop database.")
            cursor.close()
            return True

        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            try:
                self.conn.rollback()
                cursor.close()
            except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error2:
                logging.error("Another error occurred during shutdown. There might be data loss.")
                logging.error(error2)
            raise AttributeError("Error during database operation. Check if there is an active connection.")

    def _fire_query(self, query: str, tuples: List[Tuple]) -> bool:
        """
        Sends the query enriched with dataframe entries to the connected database server.

        :param query: the query itself with placeholders
        :param tuples: the data which will be inserted into the query
        :return: True if the query was successfully carried out
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            # Select database schema and execute query on it
            cursor.execute(f"SET search_path TO {self.DB_SCHEMA}")
            cursor.executemany(query, tuples)
            self.conn.commit()
            logging.info("Successfully performed query.")
            cursor.close()
            return True
        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.error(f"Failed to perform query: \n Query: {query}")
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            try:
                self.conn.rollback()
                cursor.close()
            except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error2:
                logging.error("Another error occurred during shutdown/rollback. There might be data corruption.")
                logging.error(error2)
            raise AttributeError("Error during database operation. Check if there is an active connection.")

    def save(self, table: OmopTableEnum, df: pd.DataFrame) -> bool:
        """
        save the DataFrame in the given OMOP table

        :param table: the df should be stored
        :param df: with OMOP data
        """
        logging.info(f"Saving Table {table.value}.")
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = f"INSERT INTO {table.value}({cols}) VALUES({','.join(['%s'] * len(df.columns))})"

        try:
            return self._fire_query(query, tuples)

        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.error(f"Failed to perform query: \n Query: {query}")
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            raise AttributeError("Error during database operation. Check if there is an active connection.")

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

        if code == 'U09' or code == 'U09.9' or code == 'U08' or code == 'U08.9' or code == 'U07.1':
            # (post) Covid (in personal history)
            return SnomedConcepts.COVID_19.value
        elif code == 'U07.2':
            # Covid (suspected)
            return SnomedConcepts.COVID_19_VIRUS_NOT_IDENTIFIED.value

        cursor = None

        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SET search_path TO {self.DB_SCHEMA}")
            # Get Omop - Concept Id of the given code
            cursor.execute(
                f"SELECT concept_id FROM concept WHERE concept_code = '{code}' AND vocabulary_id = '{vocabulary_id}';")
            concept_id_original = cursor.fetchone()[0]

            # Get Concept Id of according Snomed Concept
            cursor.execute(
                f"SELECT concept_id_2 FROM concept_relationship WHERE relationship_id = 'Maps to' "
                f"AND concept_id_1 = '{concept_id_original}';")
            concept_id_snomed = int(cursor.fetchone()[0])
            cursor.close()

        except TypeError:
            # Set to 0 if no mapping was found, means 'No matching concept' in omop vocabulary
            concept_id_snomed = 0
            logging.debug(f"Could not find a mapping for {code} in {vocabulary_id}.")

        except (Exception, psycopg2.DatabaseError, AttributeError, ValueError) as error:
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            try:
                cursor.close()
            except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error2:
                logging.error("Another error occurred during shutdown/rollback. There might be data corruption.")
                logging.error(error2)
            raise AttributeError("Error during database operation. Check if there is an active connection.")

        return concept_id_snomed

    def send_query(self, query: str) -> pd.DataFrame:
        """
        Sends the given query to the database and returns a dataframe of the results.
        No further enriching is performed on the given query. If the query leads to an error 'None' is returned.

        :param query: the query
        :return: a pandas DataFrame with the results or 'None'
        """
        cursor = None

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = pd.read_sql_query(query, self.conn)
            cursor.close()
            return result
        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.debug(f"Error executing query: {query}")
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            try:
                self.conn.rollback()
                cursor.close()
            except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error2:
                logging.error("Another error occurred during shutdown. There might be data loss.")
                logging.error(error2)
            raise AttributeError("Error during database operation. Check if there is an active connection.")

    def generate_condition_occurrence_id(self) -> int:
        """
        Generates a unique identifier that is not already taken by an entry in the condition_occurrence table.

        :return: an integer that is currently not used by the condition-occurrence table as an id
        """
        # Generates a random number until no match is found in the condition occurrence table
        new_id = randrange(10000, 9999999)
        while self._id_is_taken(OmopTableEnum.CONDITION_OCCURRENCE.value,
                                OmopConditionOccurrenceFieldsEnum.CONDITION_OCCURRENCE_ID.value,
                                new_id):
            new_id = randrange(10000, 9999999)
        return new_id

    def generate_patient_id(self) -> int:
        """
        Generates a unique identifier that is not already taken by an entry in the person table.

        :return: an integer that is currently not used by the person table as an id
        """
        new_id = randrange(10000, 9999999)
        while self._id_is_taken(OmopTableEnum.PERSON.value, OmopPersonFieldsEnum.PERSON_ID.value, new_id):
            new_id = randrange(10000, 9999999)
        return new_id

    def _id_is_taken(self, table: str, field: str, new_id: int) -> bool:
        """
        Checks if the given id is taken by an entry for the given field of the given table.

        :param table: name of the table in the database
        :param field: column name that holds the ids for the table
        :param new_id: id that is checked
        :return: True if the id is already in use
        """
        query: str = f"SELECT * FROM {self.DB_SCHEMA}.{table} WHERE {field} = {new_id}"
        result_df: pd.DataFrame = self.send_query(query)
        return not result_df.empty

    def delete_condition_for_patient(self, person_id: int, condition_id: int) -> bool:
        """
        Deletes the condition with the given condition_concept_id from the person with the given person id.
        If the combination is not present in the database after the operation, True is returned. This means this method
        will return True if the combination was not present to begin with.
        If the transaction fails, this method will return false.

        :person_id: id of the person with the condition
        :condition_id: concept id of the condition
        :return: True if the condition was removed
        """
        cursor = None
        query: str = f"DELETE FROM {self.DB_SCHEMA}.{OmopTableEnum.CONDITION_OCCURRENCE.value} " \
                     f"WHERE {OmopConditionOccurrenceFieldsEnum.PERSON_ID.value} = {person_id} " \
                     f"AND {OmopConditionOccurrenceFieldsEnum.CONDITION_CONCEPT_ID.value} = {condition_id};"
        try:
            cursor = self.conn.cursor()
            # Execute delete query
            cursor.execute(query)
            self.conn.commit()
            logging.info("Successfully performed query.")
            cursor.close()
            return True
        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.error(f"Failed to perform query: \n Query: {query}")
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            try:
                self.conn.rollback()
                cursor.close()
            except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error2:
                logging.error("Another error occurred during shutdown. There might be data loss.")
                logging.error(error2)
            raise AttributeError("Error during database operation. Check if there is an active connection.")

    def update_person_field(self, person_id: int, field: str, value):
        """
        Updates the entry of the person with the given id. The value of the field with the given field-name will be
        overwritten with provided value:

        :param person_id: id of the person that will be updated
        :param field: name of the field that will be updated
        :param value: new value for that field
        """
        cursor = None
        query: str = f"UPDATE {self.DB_SCHEMA}.{OmopTableEnum.PERSON.value} SET {field} = '{value}' " \
                     f"WHERE {OmopPersonFieldsEnum.PERSON_ID.value} = {person_id};"
        try:
            cursor = self.conn.cursor()
            # Execute update query
            cursor.execute(query)
            self.conn.commit()
            logging.info("Successfully performed update.")
            cursor.close()
            return True
        except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error:
            logging.error(f"Failed to perform query: \n Query: {query}")
            logging.error("An error occurred during the database operation:")
            logging.error(error)
            try:
                self.conn.rollback()
                cursor.close()
            except (Exception, psycopg2.DatabaseError, AttributeError, TypeError, ValueError) as error2:
                logging.error("Another error occurred during shutdown. There might be data loss.")
                logging.error(error2)
            raise AttributeError("Error during database operation. Check if there is an active connection.")


if __name__ == "__main__":
    db_config = generate_config()[1]
    db_manager = DBManager(db_config=db_config, clear_tables=False)
    print(db_manager.get_snomed_id('M30.3', 'ICD10GM'))
