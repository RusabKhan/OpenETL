"""
This module contains utility functions for working with data schema and types.

Classes:
- SchemaUtils: A class for working with data schema and types.

Functions:
- match_pandas_schema_to_spark: Matches the data types of columns in a Spark DataFrame to a specified schema.
- commit_changes: Commits the changes made within the session.
- __enter__: Enters the `with` context and creates a new session.
- close_session: Closes the session and sets the session close flag.
- __exit__: Exits the `with` context, commits changes, and closes the session.
- create_table: Creates a new table in the database. If the table already exists, it skips the creation.
- __init__: Initializes the class with the given connection credentials.
"""
import pandas as pd
import time
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Float, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from utils.cache import sqlalchemy_database_engines
from sqlalchemy.exc import OperationalError
from utils.enums import ColumnActions
import numpy as np
from pyspark.sql.types import StringType, IntegerType, FloatType, DoubleType, BooleanType, TimestampType, DateType, ArrayType, MapType
import re


class SchemaUtils:
    is_session_close = True

    def __init__(self, connection_creds: dict):
        """
        Initialize the class with the given connection credentials.

        Parameters:
            connection_creds (dict): A dictionary containing the connection credentials.

        Returns:
            None
        """

        engine = connection_creds['ENGINE']
        self._create_engine(engine, connection_creds)
        self.metadata = MetaData()
        self.schema_details = {}

    # TO CREATE ENGINE
    def _create_engine(self, engine, connection_creds):
        """
        Create a database engine based on the provided engine type and connection credentials.

        Parameters:
            engine (str): The type of database engine to create.
            connection_creds (dict): A dictionary containing the connection credentials including 'USERNAME', 'PASSWORD', 'HOSTNAME', 'PORT', 'DATABASE'.

        Raises:
            ValueError: If any of the required credentials are missing in the connection_creds dictionary.
        """
        required_credentials = ['USERNAME',
                                'PASSWORD', 'HOSTNAME', 'PORT', 'DATABASE']
        database_connection = sqlalchemy_database_engines.get(engine)
        missing_credentials = [
            cred for cred in required_credentials if cred not in connection_creds]

        if missing_credentials:
            raise ValueError(
                f"Missing connection credentials: {', '.join(missing_credentials)}")

        username = connection_creds['USERNAME']
        password = connection_creds['PASSWORD']
        host_ip = connection_creds['HOSTNAME']
        port = connection_creds['PORT']
        database = connection_creds['DATABASE']

        connection_string = f"{database_connection}://{username}:{password}@{host_ip}:{port}/{database}"
        self._engine = create_engine(connection_string)

    # TO HANDLE DML TASKS

    def dataframe_details(self, df):
        """
        Generate a dictionary containing details about each column in the DataFrame.

        Parameters:
            df (DataFrame): The input DataFrame for which details are to be generated.

        Returns:
            dict: A dictionary where keys are column names and values are their data types.
        """
        details = {}
        for col in df.columns:
            dtype = df[col].dtype.name
            # Mapping Pandas data types to SQLAlchemy data types
            if dtype == 'float64':
                dtype = 'Float'
            elif dtype == 'int64':
                dtype = 'Integer'
            elif dtype == 'bool':
                dtype = 'Boolean'
            elif dtype == 'object':
                dtype = 'String'
            elif dtype == 'datetime64[ns]':
                dtype = 'DateTime'
            elif dtype == 'timedelta64[ns]':
                dtype = 'Interval'
            elif dtype == 'category':
                dtype = 'Enum'
            elif dtype == 'bytes':
                dtype = 'LargeBinary'
            elif dtype == 'unicode':
                dtype = 'UnicodeText'
            elif dtype == 'period':
                dtype = 'Interval'
            elif dtype == 'object':
                if df[col].apply(lambda x: isinstance(x, dict)).any():
                    dtype = 'Dictionary'
                elif df[col].apply(lambda x: isinstance(x, list)).any():
                    dtype = 'Array'
            else:
                dtype = 'String'
            details[col] = str(dtype)
        return details

    def create_table(self, table_name: str, df: pd.DataFrame):
        """
        Create a new table in the database. If already exists, skip creation.

        Args:
            table_name (str): The name of the table.
            schema_details (dict): column_name with python datatypes. Valid values are `str`, `float`, `bool`, `int`, `list`.
        Returns:
            tuple: A tuple indicating the success status and a message.
        """
        try:
            schema_details = self.dataframe_details(df)
            table = Table(table_name, self.metadata,
                          *[Column(column_name, eval(column_type)) for column_name, column_type in schema_details.items()])
            self.metadata.create_all(self._engine)

            self.schema_details = schema_details

            return True, table_name
        except Exception as e:
            return False, str(e)

    def fill_na_based_on_dtype(self, df):
        """
        Replace NaN values in a Pandas DataFrame based on the data type of each column.

        Parameters:
            df: Pandas DataFrame.

        Returns:
            DataFrame: DataFrame with NaN values replaced based on column data types.
        """
        nan_replacements = {
            'int64': 0,
            'float64': 0.0,
            'bool': False,
            'object': ' ',
            'string': ' ',
            'datetime64[ns]': pd.Timestamp('1970-01-01'),
            'timedelta64[ns]': pd.Timedelta('0 days'),
            'category': ' ',
            'bytes': b' ',
            'unicode': u' ',
            # Add more data types as needed
        }
        nan_variations = ['nan', 'NaN', 'Nan', 'naN', 'NAN']  # Add more variations if needed
        
        for col in df.columns:
            dtype = df[col].dtype.name
            if dtype in nan_replacements:
                # Replace variations of NaN values
                df[col] = df[col].map(lambda x: nan_replacements[dtype] if str(x).strip().lower() in nan_variations else x)
        
        return df



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

    def cast_columns(self, df):
        """
        Function to cast columns in a DataFrame to specific data types based on the majority of data types in the columns.

        Parameters:
        - self: The object instance
        - df: The DataFrame containing the columns to be cast

        Returns:
        - df: The DataFrame with columns casted to specific data types
        """
        for col in df.columns:
            types_counts = {
                str: df[col].apply(lambda x: isinstance(x, str)).sum(),
                int: df[col].apply(lambda x: isinstance(x, int)).sum(),
                float: df[col].apply(lambda x: isinstance(x, float)).sum(),
                list: df[col].apply(lambda x: isinstance(x, list) or isinstance(x, np.ndarray)).sum(),
                dict: df[col].apply(lambda x: isinstance(x, dict)).sum(),
                bool: df[col].apply(lambda x: isinstance(x, bool)).sum(),
                np.datetime64: pd.api.types.is_datetime64_any_dtype(df[col]),
                np.timedelta64: pd.api.types.is_timedelta64_dtype(df[col]),
                bytes: df[col].apply(lambda x: isinstance(x, bytes)).sum()
            }
            majority_type = max(types_counts, key=types_counts.get)
            if majority_type == list or majority_type == np.ndarray:
                df[col] = df[col].apply(lambda x: list(
                    x) if isinstance(x, np.ndarray) else x).astype(str)
            elif majority_type == np.datetime64:
                df[col] = df[col].astype('datetime64[ns]')
            elif majority_type == np.timedelta64:
                df[col] = df[col].astype('timedelta64[ns]')
            else:
                df[col] = df[col].astype(majority_type)
        return df

    def map_to_spark_type(self, pandas_dtype):
        """
        Map Pandas DataFrame data types to equivalent Spark DataFrame data types.

        Parameters:
            pandas_dtype (str): Pandas DataFrame data type.

        Returns:
            Spark DataFrame data type.
        """
        spark_type_map = {
            'Object': StringType(),
            'Integer': IntegerType(),
            'Float': FloatType(),
            'Boolean': BooleanType(),
            'Datetime': TimestampType(),
            # Spark does not have a direct equivalent for timedelta
            'Interval': StringType(),
            'Enum': StringType(),  # Defaulting to StringType for Pandas categories
            'LargeBinary': StringType(),  # Defaulting to StringType for bytes
            'UnicodeText': StringType(),  # Defaulting to StringType for unicode
            'Interval': StringType(),  # Defaulting to StringType for period
            # Mapping to ArrayType with StringType elements
            'Array': ArrayType(StringType()),
            # Mapping to MapType with StringType keys and values
            'Dictionary': MapType(StringType(), StringType()),
            # Add more mappings as needed
        }
        # Default to StringType for unrecognized types
        return spark_type_map.get(pandas_dtype, StringType())

    def match_pandas_schema_to_spark(self, spark_df, schema_details=None):
        """
        Match the data types of columns in a Spark DataFrame to a specified schema.

        Parameters:
            spark_df (DataFrame): Spark DataFrame.
            schema_dict (dict): Dictionary where keys are column names and values are desired data types.

        Returns:
            DataFrame: Spark DataFrame with matched data types.
        """
        schema_details = schema_details if schema_details else self.schema_details
        for col, dtype in schema_details.items():
            spark_dtype = self.map_to_spark_type(dtype)
            spark_df = spark_df.withColumn(
                col, spark_df[col].cast(spark_dtype))
        return spark_df

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
