import sys
import os
import pandas as pd
from sqlalchemy import create_engine
from utils import AuthType

sys.path.append(os.environ['OPENETL_HOME'])

from utils.main_db_class import DB


class Connector(DB):

    def __init__(self):
        self.required_libs = ["shillelagh[gsheetsapi]"]
        self.logo = "https://upload.wikimedia.org/wikipedia/commons/5/51/Google_Cloud_logo.svg"
        self.authentication_details = {
            AuthType.BASIC: {
                "sheet_url": "",
            }
        }
        self.engine = None
        super().__init__()

    def create_engine(self, sheet_url=None, *args, **kwargs):
        """Create a connection to Google Sheets"""
        if not sheet_url:
            raise ValueError("Missing Google Sheet URL")

        self.sheet_url = sheet_url.replace("/edit#gid=", "/gviz/tq?tqx=out:csv&gid=")
        self.engine = create_engine("gsheets://")

    def test_connection(self):
        """Test if the connection to Google Sheets works"""
        if not self.engine:
            raise ValueError("Engine not initialized. Call `create_engine` first.")

        try:
            query = f'SELECT * FROM "{self.sheet_url}" LIMIT 1'
            result = pd.read_sql(query, self.engine)
            return not result.empty  # Return True if data is retrieved
        except Exception as e:
            return f"Connection failed: {e}"

    def execute_query(self, query):
        """Execute a SQL query on Google Sheets"""
        if not self.engine:
            raise ValueError("Engine not initialized. Call `create_engine` first.")

        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")

    def read_table(self, table_name=None, schema_name="public", page_size=10000):
        """Read an entire Google Sheet as a Pandas DataFrame"""
        if not self.engine:
            raise ValueError("Engine not initialized. Call `create_engine` first.")

        query = f'SELECT * FROM "{self.sheet_url}"'
        return pd.read_sql(query, self.engine)

    def close_session(self):
        """Close the SQLAlchemy session"""
        self.engine.dispose()

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure resources are cleaned up"""
        self.close_session()
