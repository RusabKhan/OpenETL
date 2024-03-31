import pandas as pd
import gspread
import time
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Float, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from utils.cache import sqlalchemy_database_engines
from sqlalchemy.exc import OperationalError
from utils.enums import ColumnActions


def get_datatypes_and_default_values(sheet_link):
    """
    Retrieves data types and default values from a Google Sheets document using SQL, then
    stores the result in a Pandas dataframe.

    :return: Pandas dataframe containing data types and default values
    """
    gc = gspread.models.Spreadsheet(
        gspread.client.Client(None), None, sheet_link)
    worksheet = gc.get_worksheet(0)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df



class SchemaUtils:
    is_session_close = True

    def __init__(self, connection_creds: dict):
        
        engine = connection_creds['engine']
        self._create_engine(engine, connection_creds)
        self.metadata = MetaData()

    # TO CREATE ENGINE
    def _create_engine(self, engine, connection_creds):
        required_credentials = ['username',
                                'password', 'host', 'port', 'database']
        database_connection = sqlalchemy_database_engines.get(engine)
        missing_credentials = [
            cred for cred in required_credentials if cred not in connection_creds]

        if missing_credentials:
            raise ValueError(
                f"Missing connection credentials: {', '.join(missing_credentials)}")

        username = connection_creds['username']
        password = connection_creds['password']
        host_ip = connection_creds['host']
        port = connection_creds['port']
        database = connection_creds['database']

        connection_string = f"{database_connection}://{username}:{password}@{host_ip}:{port}/{database}"
        self._engine = create_engine(connection_string)

    # TO HANDLE DML TASKS

    def create_table(self, table_name: str, schema_details: dict):
        """
        Create a new table in the database.

        Args:
            table_name (str): The name of the table.
            schema_details (dict): column_name with python datatypes. Valid values are `str`, `float`, `bool`, `int`, `list`.
        Returns:
            tuple: A tuple indicating the success status and a message.
        """
        try:

            table = Table(table_name, self.metadata,
                          *[Column(column_name, eval(column_type)) for column_name, column_type in schema_details.items()])
            self.metadata.create_all(self._engine)

            return True, table_name
        except Exception as e:
            return False, str(e)


    def alter_table_column_add_or_drop(self, table_name, column_name=None, column_details=None, action: ColumnActions = ColumnActions.ADD):
        """
        Alters a SQLAlchemy table by either adding or dropping a column.

        Args:
            table_name (str): The name of the table to be altered.
            metadata (MetaData): The metadata object associated with the database.
            engine (Engine): The SQLAlchemy engine object connected to the database.
            column_name (str): The name of the column to be added or dropped. Required if drop_column is False.
            column_details (str): The details of the column to be added. Required if drop_column is False.
            drop_column (bool): Indicates whether to drop the column. If True, column_name is required.

        Returns:
            tuple: A tuple containing a boolean indicating success or failure and a message.

         """
        try:
            # Reflect the existing table from the database
            table = Table(table_name, self.metadata,
                          autoload=True, autoload_with=self._engine)

            if action == ColumnActions.DROP:
                table._columns.remove(table.c[column_name])
                action = f"Dropped column '{column_name}' from table '{table_name}'."
                
            elif action == ColumnActions.ADD:
                new_column = Column(column_name, eval(column_details))
                table.append_column(new_column)
                action = f"Added column '{column_name}' to table '{table_name}'."
                
            elif action == ColumnActions.MODIFY:
                raise NotImplementedError

            # Save changes to the database
            self.metadata.drop_all(self._engine)
            self.metadata.create_all(self._engine)

            return True, action
        except OperationalError as e:
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
