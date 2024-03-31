import streamlit as st
from utils.cache import *
import sqlalchemy as sq
import pandas as pd
from sqlalchemy import text
# from .style_utils import load_css

# load_css()



class SQLAlchemyEngine():
    """A class to connect with any database using SQLAlchemy.
    """
    def __init__(self, engine, hostname, username, password, port, database, connection_name=None,connection_type=None):
        """Initialize class

        Args:
            engine (string): Sqlalchemy dialect
            hostname (string): You database hostname
            username (string): Your database username
            password (string): Your database password
            port (string): Your database port
            database (string): Your database
            connection_name (string, optional): _description_. Defaults to None.
            connection_type (string, optional): _description_. Defaults to None.
        """
        engine = sqlalchemy_database_engines[engine]
        url = f"{engine}://{username}:{password}@{hostname}:{port}/{database}"

        self.conn = sq.create_engine(
            url=url
        )

    def test(self):
        """Test connection to database

        Returns:
            Boolean: True if connected else False
        """
        try:
            self.conn.connect()
            return True
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False

    def get_metadata(self):
        """Get schema metadata from the connection

        Returns:
            dict: {"tables": tables,"schema":[]}
        """
        try:
            inspector = sq.inspect(self.conn)
            schemas = inspector.get_schema_names()
            tables = []

            for schema in schemas:
                print(f"schema: {schema}")
                tables.append(inspector.get_table_names(schema=schema))
            return {"tables": tables,"schema": schemas}
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return {"tables": tables,"schema":[]}
    
    def execute_query(self,query):
        """Execute query against the connection

        Args:
            query (string): Valid SQL query

        Returns:
            Dataframe: Pandas dataframe of your query results
        """
        try:
            con = self.conn.connect()
            data = con.execute(text(query))
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return pd.DataFrame()

    def get_metadata_df(self):
        """Get your schema metadata in a dataframe

        Returns:
            Dataframe: Pandas dataframe of your schema
        """
        inspector = sq.inspect(self.conn)
        schemas = inspector.get_schema_names()
        tables = []
        data = {}
        for schema in schemas:
            data_schema = []
            print(f"schema: {schema}")
            tables = inspector.get_table_names(schema=schema)
            data["Table Name"] = tables
            while len(tables) < len(data_schema):
                data_schema.append(schema)
            data["Schema"] = schema
        return pd.DataFrame(data)