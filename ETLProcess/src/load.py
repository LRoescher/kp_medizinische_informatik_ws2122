import psycopg2


class Loader:
    """
    Class responsible for connecting to the omop-database and loading CDM-compliant tables into it.
    """
    # TODO Use config file instead for connection parameters
    HOST: str = "localhost"
    PORT: str = "5432"
    DB_NAME: str = "OHDSI"
    USERNAME: str = "postgres"
    PASSWORD: str = "pass"
    # other constants
    OMOP_TABLE_PERSON: str = "person"
    OMOP_TABLE_LOCATION: str = "location"

    def __init__(self):
        """
        Creates a new Loader. Establishes a database connection.
        """
        self.conn = self._connect()

    def _connect(self):
        """
        Connect to the PostgreSQL database server.
        :return a connection to the database server
        """
        conn = None
        try:
            # connect to the PostgreSQL server
            print('[INFO] Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(
                host=self.HOST,
                port=self.PORT,
                database=self.DB_NAME,
                user=self.USERNAME,
                password=self.PASSWORD)
            print('[INFO] Successfully connected to the PostgreSQL database.')
        except Exception as error:
            print("[ERROR] Failed to establish connection: \n %s" % error)
        finally:
            return conn

    def _fire_query(self, query, tuples):
        """
        Sends the query enriched with dataframe entries to the connected database server.

        :param query: the query itself with placeholders
        :param tuples: the data which will be inserted into the query
        :return: True if the query was successfully carried out
        """
        cursor = self.conn.cursor()
        try:
            # Select p21_cdm schema and execute query on it
            cursor.execute("SET search_path TO p21_cdm")
            cursor.executemany(query, tuples)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("[ERROR] Failed to perform query: \n Query: %s \n Message:%s" % error)
            self.conn.rollback()
            cursor.close()
            return False
        print("[INFO] Successfully performed query.")
        cursor.close()
        return True

    def save_location(self, df):
        print("[INFO] Saving Table %s." % self.OMOP_TABLE_LOCATION)
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % (self.OMOP_TABLE_LOCATION, cols)
        self._fire_query(query, tuples)

    def save_person(self, df):
        print("[INFO] Saving Table %s." % self.OMOP_TABLE_PERSON)
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s, %%s, %%s, %%s)" % (
            self.OMOP_TABLE_PERSON, cols)
        self._fire_query(query, tuples)
