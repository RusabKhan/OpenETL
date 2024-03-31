import streamlit as st
from utils.cache import *
from .style_utils import load_css
import jaydebeapi
import zipfile
import requests
import sys
from .local_connection_utils import check_jar_exists
import os
import pandas as pd
load_css()


class JDBCEngine():

    sys.path.append('../')
    conn = None

    def __init__(self, engine, hostname, username, password, port, connection_name=None, database=None,connection_type=None):

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
