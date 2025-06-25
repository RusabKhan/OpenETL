from openetl_utils.main_db_class import DB


class Connector(DB):
    
    def __init__(self):
        self.required_libs = ["psycopg2-binary==2.9.9"]
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/postgresql-icon.svg"
        self.engine = "PostgreSQL"
        super().__init__()



    def create_engine(self, hostname, username, password, port, database, connection_name=None, connection_type=None,engine="PostgreSQL", schema="public", **kwargs):
        return super().create_engine(engine, hostname, username, password, port, database, connection_name=None, connection_type=None, schema=schema)
        
    def test_connection(self):
        return super().test_connection()
    
    def get_metadata(self, *args, **kwargs):
        auth_details = kwargs
        return super().get_metadata(**auth_details)
    
    def execute_query(self, query):
        return super().execute_query(query)
    
    def write_data(self, data, table_name, if_exists='append', schema="public"):
        return super().write_data(data, table_name, if_exists, schema)
    
    def close_session(self):
        super().close_session()
    
    def read_table(self, table_name, schema_name="public", page_size=10000):
        return super().read_table(table_name, schema_name, page_size)
    
    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        
