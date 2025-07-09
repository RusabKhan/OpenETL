import sys
import os

from openetl_utils import AuthType

sys.path.append(os.environ['OPENETL_HOME'])

from openetl_utils.main_db_class import DB



class Connector(DB):
    
    def __init__(self):
        self.required_libs = ["pymysql==1.1.0"]
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/mysql-icon.svg"
        self.engine = "MySQL"
        self.authentication_details = {
            AuthType.BASIC: {
                "hostname": "",
                "username": "",
                "password": "",
                "database": "",
                "schema": "",
            }
        }
        super().__init__()

    def create_engine(self, hostname, username, password, port, database, connection_name=None, connection_type=None,engine="MySQL", schema="defaultdb", **kwargs):
        return super().create_engine(engine, hostname, username, password, port, database, connection_name=None,
                                     connection_type=None, schema=schema)
        
    def get_metadata(self, *args, **kwargs):
        auth_details = kwargs
        return super().get_metadata(**auth_details)
    
    def get_metadata(self):
        return super().get_metadata()
    
    def execute_query(self, query):
        return super().execute_query(query)
    
    def write_data(self, data, table_name, if_exists='append', schema="public"):
        return super().write_data(data, table_name, if_exists, schema)
    
    def close_session(self):
        super().close_session()

    def test_connection(self):
        return super().test_connection()
    
    def read_table(self, table_name, schema_name="public", page_size=10000):
        return super().read_table(table_name, schema_name, page_size)
    
    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        
