"""
This module contains utility functions for working with SQLAlchemy engine connections.

Class:
- SQLAlchemyEngine: Represents a class to connect with any database using SQLAlchemy.

Methods:
- __init__: Initializes the class with database connection details.
- test: Tests the connection to the database.
- get_metadata: Retrieves schema metadata from the connection.
- execute_query: Executes a SQL query against the connection.
- get_metadata_df: Retrieves schema metadata in a dataframe format.
"""
import pandas as pd
from sqlalchemy import MetaData, Table
from openetl_utils.database_utils import DatabaseUtils
from openetl_utils.connector_utils import install_libraries
from openetl_utils.enums import ConnectionType, AuthType
import logging

class DB(DatabaseUtils):
    """A class to connect with any database using SQLAlchemy.
    """

    required_libs = []
    connection_type = ConnectionType.DATABASE
    authentication_details = {AuthType.BASIC: {
        "username": "",
        "password": "",
        "hostname": "",
        "port": 0,
        "database": "",
        "schema": "public",
    }}

    def __init__(self):
        self.install_missing_libraries()


    def create_engine(self, engine, hostname, username, password, port, database, connection_name=None, connection_type=None, schema="public"):
        if hostname is not None and username is not None and password is not None and port is not None and database is not None:
            super().__init__(engine, hostname, username, password, port, database, connection_name, connection_type, schema=schema)


    def test_connection(self) -> bool:
        """Test connection to database

        Returns:
            Boolean: True if connected else False
        """
        return super().test()

    def get_metadata(self)->dict:
        """Get schema metadata from the connection

        Returns:
            dict: {"tables": tables,"schema":[]}
        """
        return super().get_metadata()
    
    def execute_query(self, query) -> pd.DataFrame:
        """Execute query against the connection

        Args:
            query (string): Valid SQL query

        Returns:
            Dataframe: Pandas dataframe of your query results
        """
        return super().execute_query(query)



    def write_data(self, data, table_name, if_exists='append', schema="public") -> bool:
        """
        Writes data to a table in etl_batches.

        Parameters:
            df (DataFrame): The DataFrame to write to the table.
            table_name (str): The name of the table to write to.
        """
        return super().write_data(data, table_name, if_exists, schema)


    def close_session(self) -> None:
        """
        Close the session and set the session close flag.
        """
        super().close_session()

    # TO HANDLE `with` CONTEXT MANAGER


    def __exit__(self, exc_type, exc_value, traceback)->None:
        """
        Exit the `with` context and commit changes, close the session.
        """
        super().__exit__(exc_type, exc_value, traceback)



    def read_table(self, table_name,schema_name="public", page_size=10000) -> pd.DataFrame:
        """
        Read data from a table in etl_batches.

        Parameters:
            table_name (str): The name of the table to read from.
            page_size (int, optional): The number of rows to read per page. Defaults to 10000.

        Returns:
            pandas.DataFrame: The DataFrame containing the data from the table.
        """
        try:
            table_name = f"{schema_name}.{table_name}"

            metadata = MetaData()
            metadata.reflect(self.engine, schema=schema_name)
            table = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
            
            select_query = table.select()
            
            dfs = []
            offset = 0
            
            while True:
                page_query = select_query.offset(offset).limit(page_size)
                df = pd.read_sql(page_query, self.engine)
                dfs.append(df)
                
                offset += page_size
                if len(df) < page_size:
                    break
            
            result_df = pd.concat(dfs, ignore_index=True)
            return result_df

        except Exception as e:
            logging.error(e)
            return pd.DataFrame(columns=["error"], data=[str(e)])


    def install_missing_libraries(self) -> bool:
        """
        Checks if there are any missing libraries required for the function to run. If there are missing libraries, it calls the install_libraries function to install them. 

        :return: True if the libraries are installed successfully, False otherwise.
        """
        if len(self.required_libs) > 0:
            return install_libraries(self.required_libs)
        
    def get_metadata(self, *args, **kwargs) -> dict:
        """
        Returns the metadata for the API.

        Returns:
            dict: A dictionary containing the metadata for the API.
        """
        self.create_engine(**kwargs)
        return super().get_metadata()