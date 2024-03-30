import pandas as pd
import gspread
import time
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from local.cache import sqlalchemy_database_engines


def get_datatypes_and_default_values(sheet_link):
    """
    Retrieves data types and default values from a Google Sheets document using SQL, then
    stores the result in a Pandas dataframe.

    :return: Pandas dataframe containing data types and default values
    """
    gc = gspread.models.Spreadsheet(gspread.client.Client(None), None, sheet_link)
    worksheet = gc.get_worksheet(0)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


DATA_TYPE_MAPPING = {
    str: String(255),
    bool: Boolean,
    int: Integer,
    float: Float,
    list: String(255)
}

class SchemaUtils:
    is_session_close = True
    
    def __init__(self, database_name: str, connection_creds: dict):
        self._create_engine(database_name, connection_creds)
    
    # TO CREATE ENGINE
    def _create_engine(self, database_name, connection_creds):
        required_credentials = ['username', 'password', 'host', 'port', 'database']
        database_connection = sqlalchemy_database_engines.get(database_name) 
        missing_credentials = [cred for cred in required_credentials if cred not in connection_creds]

        if missing_credentials:
            raise ValueError(f"Missing connection credentials: {', '.join(missing_credentials)}")

        username = connection_creds['username']
        password = connection_creds['password']
        host_ip = connection_creds['host']
        port = connection_creds['port']
        database = connection_creds['database']
        
        connection_string = f"{database_connection}://{username}:{password}@{host_ip}:{port}/{database}"
        self._engine = create_engine(connection_string) 
    
    # TO HANDLE DYNAMIC TABLE
    def create_dynamic_table(self, table_name: str):
        """
        Create a dynamic table class with the provided table name.

        Args:
            table_name (str): The name of the table.

        Returns:
            class: The dynamically created table class.
        """
        
        class_name = f"DynamicTable_{table_name}"

        if class_name in self.metadata.tables:
            DynamicTable = self.metadata.tables[class_name]
        else:
            DynamicTable = type(class_name, (self.Base,), {
                '__tablename__': table_name,
                'id': Column(Integer, primary_key=True)
            })

        return DynamicTable

    # TO HANDLE DML TASKS
    def create_table(self, table_name: str, json_data: dict):
        """
        Create a new table based on the provided table name and JSON data.

        Args:
            table_name (str): The name of the table.
            json_data (dict): The JSON data containing column names and values.

        Returns:
            tuple: A tuple indicating the success status and a message.
        """
        try:
            DynamicTable = self.create_dynamic_table(table_name)

            for key, value in json_data.items():
                data_type = DATA_TYPE_MAPPING.get(type(value), String(255))
                setattr(DynamicTable, key, Column(data_type))
                    
            self.Base.metadata.create_all(self._engine)
            
            print(f"Table '{table_name}' created.")
            return True, f"Table '{table_name}' created."
        except Exception as e:
            return False, str(e)

    def alter_table(self, table_name: str, columns: dict):
        """
        Alter the specified column in the database table.

        Args:
            table_name (str): The name of the table.
            columns (dict): column_name with python datatypes. Valid values are `str`, `float`, `bool`, `int`, `list`.
        Returns:
            tuple: A tuple indicating the success status and a message.
        """
        try:
            self.metadata.reflect(bind=self._engine, only=[table_name])
            existing_table = self.metadata.tables.get(table_name, False)
            
            if existing_table:
                altered_columns = dict()
                DynamicTable = self.create_dynamic_table(existing_table)
                for column_name, data_type in columns.items():
                    mapped_data_type = DATA_TYPE_MAPPING.get(data_type, String(255))
                    setattr(DynamicTable, column_name, Column(column_name, mapped_data_type))
                    altered_columns[column_name] = mapped_data_type
                
                DynamicTable.__table__.create(bind=self._engine, checkfirst=True)
                
                return True, f"`{table_name}` altered columns `{str(list(altered_columns.keys()))}` with datatypes: `{str(list(altered_columns.values()))}`"
            else:
                return False, f"`{table_name}` doesn't exist in the Database"
        except Exception as e:
            return False, str(e)
        
    def drop_table(self, table_name: str):
        """
        Drop the specified table from the database.

        Args:
            table_name (str): The name of the table to drop.
        
        Returns:
            tuple: A tuple indicating the success status and a message.
        """
        try:
            self.metadata.reflect(bind=self._engine, only=[table_name])
            existing_table = self.metadata.tables[table_name]
            existing_table.drop(self._engine)
            
            return True, f"Table '{table_name}' has been dropped."
        except Exception as e:
            return False, str(e)

    def truncate_table(self, table_name):
        """
        Truncates a table by deleting all rows.

        Args:
            table_name (str): The name of the table to truncate.

        Returns:
            tuple: A tuple indicating the success status and a message.
                   The success status is True if truncation is successful, False otherwise.
                   The message provides information about the truncation result.
        """
        try:
            self.metadata.reflect(bind=self._engine, only=[table_name])
            table = self.metadata.tables[table_name]
            with self._engine.connect() as connection:
                delete_statement = table.delete()
                connection.execute(delete_statement)
            
            return True, f"Table '{table_name}' truncated."
        except Exception as e:
            return False, str(e)

    # TO HANDLE SESSIONS 
    def create_session(self):
        """
        Create a new session and initialize metadata and base.
        """
        Session = sessionmaker(bind=self._engine)
        self.session = Session()
        self.Base = declarative_base()
        self.metadata = MetaData()
        
        self.is_session_close = False
        return True
        
    def commit_changes(self):
        """
        Commit the changes made within the session.
        """
        self.session.commit()

    def close_session(self):
        """
        Close the session and set the session close flag.
        """
        self.session.close()
        self.is_session_close = True
    
    # TO HANDLE `with` CONTEXT MANAGER
    def __enter__(self):
        """
        Enter the `with` context and create a new session.
        """
        self.create_session()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the `with` context and commit changes, close the session.
        """
        self.commit_changes()
        self.close_session()
