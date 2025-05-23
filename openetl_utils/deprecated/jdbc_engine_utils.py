import streamlit as st
import jaydebeapi
import zipfile
import requests
import sys
from openetl_utils.local_connection_utils import check_jar_exists
import os
import pandas as pd



class JDBCEngine():

    sys.path.append('../../')
    conn = None

    def __init__(self, engine, hostname, username, password, port, connection_name=None, database=None,connection_type=None):

        """
        Initialize a JDBCEngine instance and establish a JDBC database connection.
        
        This constructor parses the provided engine identifier to extract Maven artifact details,
        ensures that the corresponding JDBC driver JAR exists locally (downloading it if necessary),
        retrieves the JDBC driver class from the JAR, constructs a proper connection string, and
        attempts to connect to the target database using jaydebeapi. Any exceptions during connection
        establishment are caught and logged via streamlit's error display.
        
        Parameters:
            engine (str): Identifier for the JDBC engine. Must correspond to a key in the jdbc_database_engines
                mapping, with a value formatted as "artifact_group:artifact_name:artifact_version".
            hostname (str): Host address of the database server.
            username (str): Username for database authentication.
            password (str): Password for database authentication.
            port (int or str): Port number on which the database server listens.
            connection_name (Optional[str]): Optional name for the connection (unused in connection string). Defaults to None.
            database (Optional[str]): Name of the database to connect to; used in constructing the JDBC URL. Defaults to None.
            connection_type (Optional[Any]): Optional parameter to specify additional connection options. Defaults to None.
        
        Side Effects:
            - Downloads the JDBC driver JAR from Maven if it does not exist in the local ".local/jars" directory.
            - Sets the instance attribute 'conn' to a live database connection if successful.
            - Displays an error message using streamlit if the connection attempt fails.
        """
        artifact_group, artifact_name, artifact_version  = jdbc_database_engines[engine].split(":")
        save_as = f"{artifact_name}-{artifact_version}.jar"
        jar_loc = f"{os.getcwd()}/.local/jars/{save_as}"
        
        if not check_jar_exists(save_as):
            self.download_jar_from_maven(artifact_group=artifact_group,artifact_id=artifact_name,artifact_version=
                                         artifact_version, destination_path=jar_loc)

        driver_classname = self.fetch_driver_classpath(jar_loc)

        connection_string = f"jdbc:{artifact_name}://{hostname}:{port}/{database}?user={username}&password={password}"

        try:
            self.conn = jaydebeapi.connect(driver_classname, connection_string,
                                           [username, password],
                                           jar_loc)
        except Exception as e:
            st.error(f"Error: {str(e)}")


    def test(self):
        return self.conn is not None


    def download_jar_from_maven(self, artifact_group, artifact_id, artifact_version, destination_path):
        # Maven Repository URL
        try:
            url = f"https://repo1.maven.org/maven2/{artifact_group.replace('.', '/')}/{artifact_id}/{artifact_version}/{artifact_id}-{artifact_version}.jar"

            # Send a GET request to the Maven Repository URL
            response = requests.get(url)

            # Save the response content to a file
            with open(destination_path, 'wb') as file:
                file.write(response.content)

            print("JAR file downloaded successfully.")
        except Exception as e:
            print("Unable to Download JAR file from Maven Repository : EXCEPTION ::", e)


    def fetch_driver_classpath(self, jar_file_path):
        with zipfile.ZipFile(jar_file_path) as jar_file:
            manifest = jar_file.read(
                "META-INF/services/java.sql.Driver").decode("utf-8")
        main_class = None
        for line in manifest.splitlines():
            main_class = line

        if main_class:
            return main_class
        else:
            return None


    def get_metadata(self):

        schemas = []
        schema_tables_metadata = {}

        resultset = self.conn.jconn.getMetadData().getSchemas()
        cur = self.conn.cursor()
        cur._rs = resultset
        cur._meta = resultset.getMetadata()
        result_list = cur.fetchall()

        # Appending schema names inside schemas list
        [schemas.append(str(schema[0]))
         for schema in result_list if schema[0] not in schemas]

        # fetching tables metadata inisde each schema
        for schema in schemas:
            tables = []
            resultset = self.conn.jconn.getMetaData.getTables(
                None, schema, "%", None
            )
            cur = self.conn.cursor()
            cur._rs = resultset
            cur._meta = resultset.getMetaData()
            result_list = cur.fetchall()

            [tables.append(str(table[2]))
             for table in result_list if table[0] not in tables]

            schema_tables_metadata.update({
                schema: tables
            })

        return schema_tables_metadata


    def execute_query(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)

                # generating DataFrame Based on Column names
            dataset = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(dataset, columns=columns)
 

        except Exception as e:
            st.error(f"Error: {str(e)}")
            return pd.DataFrame()
