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
import calendar
import os
import sys
from typing import List, Type

import sqlalchemy
import sqlalchemy as sq
import pandas as pd
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext

from openetl_utils.__migrations__.app import OpenETLDocument, OpenETLOAuthToken
from openetl_utils.__migrations__.batch import OpenETLBatch
from openetl_utils.__migrations__.scheduler import OpenETLIntegrations, OpenETLIntegrationsRuntimes
from sqlalchemy import MetaData, Table, Column, and_, select, PrimaryKeyConstraint, func, text, inspect, or_, String, \
    desc
from sqlalchemy.orm import sessionmaker

from openetl_utils.cache import sqlalchemy_database_engines
from openetl_utils.enums import ConnectionType
from sqlalchemy.exc import OperationalError, NoResultFound
from openetl_utils.enums import ColumnActions
import numpy as np
from sqlalchemy.ext.declarative import declarative_base
from pyspark.sql.types import StringType, IntegerType, FloatType, BooleanType, TimestampType, ArrayType, MapType
from datetime import datetime, timedelta
from sqlalchemy.schema import CreateSchema
import logging
from croniter import croniter

class DatabaseUtils():
    
    """
    A class to connect with any database using SQLAlchemy.

    Attributes:
    - engine (string): Sqlalchemy dialect
    - hostname (string): Your database hostname
    - username (string): Your database username
    - password (string): Your database password
    - port (string): Your database port
    - database (string): Your database
    - connection_name (string, optional): Description of the connection. Defaults to None.
    - connection_type (string, optional): Description of the connection type. Defaults to None.

    Methods:
    - __init__: Initializes the class with database connection details.
    - test: Tests the connection to the database.
    - get_metadata: Retrieves schema metadata from the connection.
    - execute_query: Executes a SQL query against the connection.
    - get_metadata_df: Retrieves schema metadata in a dataframe format.
    - dataframe_details: Generates details about each column in a DataFrame.
    - create_table: Creates a new table in the database.
    - fill_na_based_on_dtype: Replaces NaN values in a DataFrame based on column data types.
    - alter_table_column_add_or_drop: Alters a table by adding or dropping a column.
    - drop_table: Drops the specified table from the database.
    - truncate_table: Truncates a table by deleting all rows.
    - cast_columns: Casts columns in a DataFrame to specific data types.
    - map_to_spark_type: Maps Pandas DataFrame data types to Spark DataFrame data types.
    - match_pandas_schema_to_spark: Matches data types of columns in a Spark DataFrame to a specified schema.
    - write_data: Writes data to a table in the database.
    - create_session: Creates a new session and initializes metadata and base.
    - commit_changes: Commits the changes made within the session.
    - close_session: Closes the session and sets the session close flag.
    - __enter__: Enters the 'with' context and creates a new session.
    - __exit__: Exits the 'with' context, commits changes, and closes the session.
    - __dispose__: Disposes the session and engine.
    - create_schema_if_not_exists: Creates a schema in the database if it does not already exist.
    - alter_table_column_add_primary_key: Alters a table by adding a primary key to a specified column.
    - create_document_table: Creates a document table in the database.
    - create_batch_table: Creates a batch table in the database.
    - fetch_rows: Executes a select query on the specified table with provided conditions.
    - fetch_document: Fetches a single document based on the specified table, schema, and conditions.
    - write_document: Writes a document to the specified table in the database.
    - get_created_connections: Returns a list of created connections for the specified connector type.
    - insert_openetl_batch: Inserts a new OpenETLBatch instance into the database.
    - update_openetl_batch: Updates an OpenETLBatch instance in the database.
    - get_dashboard_data: Retrieves dashboard data including total counts and integration details.
    """

    _connections = {}  # Class-level dictionary to store connections

    def __init__(self, engine=None, hostname=None, username=None, password=None, port=None, database=None,
                 connection_name=None, connection_type=None, schema="public"):
        """
                 Initialize a DatabaseUtils instance with the specified database connection parameters.
                 
                 If an engine is provided, this method generates a unique connection key based on the engine, hostname, port, database, and username. It then checks the class-level _connections dictionary for an existing engine corresponding to this key. If found, the existing engine is reused; otherwise, a new SQLAlchemy engine is created using a URL constructed from the provided details and the dialect mapping from sqlalchemy_database_engines, and it is stored in _connections. Finally, a SQLAlchemy session is created by calling self.create_session().
                 
                 If engine is None, the instance’s engine is set to None and session creation is skipped.
                 
                 Parameters:
                     engine (str, optional): Identifier for the SQLAlchemy database dialect (e.g., 'postgresql', 'mysql'). If None, no database connection will be established.
                     hostname (str, optional): The hostname of the database server.
                     username (str, optional): The username for authentication with the database.
                     password (str, optional): The password for authentication with the database.
                     port (str, optional): The port number on which the database server is listening.
                     database (str, optional): The name of the target database.
                     connection_name (str, optional): A custom name for the connection. Defaults to None.
                     connection_type (str, optional): A description of the connection type. Defaults to None.
                 """
        self.schema = schema

        if engine is None:
            self.engine = None
            return

        self.connection_key = f"{engine}_{hostname}_{port}_{database}_{username}"

        if self.connection_key in DatabaseUtils._connections:
            self.engine = DatabaseUtils._connections[self.connection_key]
        else:
            engine_dialect = sqlalchemy_database_engines[engine]
            url = f"{engine_dialect}://{username}:{password}@{hostname}:{port}/{database}"
            self.engine = sq.create_engine(url=url)

            DatabaseUtils._connections[self.connection_key] = self.engine

        self.create_session()

    def test(self):
        """
        Tests the database connection by attempting to establish a connection using the configured SQLAlchemy engine.
        
        This method calls self.engine.connect() to verify that a connection to the database can be opened. If the connection attempt fails, an exception raised by the SQLAlchemy engine will propagate. On success, it returns True.
        
        Returns:
            bool: True if the connection was successfully established.
        """
        self.engine.connect()
        return True

    def get_metadata(self):
        """Get schema metadata from the connection

        Returns:
            dict: {"tables": tables,"schema":[]}
        """
        inspector = sq.inspect(self.engine)
        schemas = inspector.get_schema_names()
        tables = None

        for schema in schemas:
            print(f"schema: {schema}")
            tables = inspector.get_table_names(schema=schema)
        return {schema: tables}

    def execute_query(self, query):
        """Execute query against the connection

        Args:
            query (string): Valid SQL query

        Returns:
            Dataframe: Pandas dataframe of your query results
        """
        con = self.engine.connect()
        data = con.execute(text(query))
        return pd.DataFrame(data)

    def get_metadata_df(self):
        """Get your schema metadata in a dataframe

        Returns:
            Dataframe: Pandas dataframe of your schema
        """
        inspector = sq.inspect(self.engine)
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

    def create_table(self, table_name: str, df: pd.DataFrame, target_schema="public"):
        """
        Create a new table in the database. If already exists, skip creation.

        Args:
            table_name (str): The name of the table.
            schema_details (dict): column_name with python datatypes. Valid values are `str`, `float`, `bool`, `int`, `list`.
        Returns:
            tuple: A tuple indicating the success status and a message.
        """
        schema_details = self.dataframe_details(df)
        table = Table(table_name, self.metadata,
                      *[Column(column_name, eval(column_type)) for column_name, column_type in schema_details.items()], schema=target_schema)
        self.metadata.create_all(self.engine)

        self.schema_details = schema_details

        return True, table_name

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
        # Add more variations if needed
        nan_variations = ['nan', 'NaN', 'Nan', 'naN', 'NAN']

        for col in df.columns:
            dtype = df[col].dtype.name
            if dtype in nan_replacements:
                # Replace variations of NaN values
                df[col] = df[col].map(lambda x: nan_replacements[dtype] if str(
                    x).strip().lower() in nan_variations else x)

        return df

    def alter_table_column_add_or_drop_alembic(self, table_name, column_name=None,
                                               column_details: sqlalchemy.Column = Column(String),
                                               action: ColumnActions = ColumnActions.ADD):
        """
        Uses Alembic Operations API to add or drop a column from a table without dropping data.
        """
        with self.engine.connect() as conn:
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)

            if action == ColumnActions.ADD:
                if not isinstance(column_details, Column):
                    return False, "column_details must be a SQLAlchemy Column instance"
                op.add_column(table_name, column_details)
                conn.commit()
                return True, f"Added column '{column_details.name}' to table '{table_name}'"

            elif action == ColumnActions.DROP:
                op.drop_column(table_name, column_name)
                conn.commit()
                return True, f"Dropped column '{column_name}' from table '{table_name}'"


            elif action == ColumnActions.MODIFY:
                if not isinstance(column_details, Column):
                    return False, "column_details must be a SQLAlchemy Column instance"
                op.alter_column(
                    table_name=table_name,
                    column_name=column_name,
                    type_=column_details.type,
                    existing_type=column_details.type,
                    nullable=column_details.nullable
                )
                conn.commit()
                return True, f"Modified column '{column_name}' in table '{table_name}'"

            else:
                return False, "Invalid action specified"

    def drop_table(self, table_name: str):
        """
        Drop the specified table from the database.

        Args:
            table_name (str): The name of the table to drop.

        Returns:
            tuple: A tuple indicating the success status and a message.
        """
        self.metadata.reflect(bind=self.engine, only=[table_name])
        existing_table = self.metadata.tables[table_name]
        existing_table.drop(self.engine)

        return True, f"Table '{table_name}' has been dropped."

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
        self.metadata.reflect(bind=self.engine, only=[table_name])
        table = self.metadata.tables[table_name]
        with self.engine.connect() as connection:
            delete_statement = table.delete()
            connection.execute(delete_statement)

        return True, f"Table '{table_name}' truncated."

    def cast_columns(self, df):
        """
        Function to cast columns in a DataFrame to specific data types based on the majority of data types in the columns.

        Parameters:
        - self: The object instance
        - df: The DataFrame containing the columns to be cast

        Returns:
        - df: The DataFrame with columns cast to specific data types
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
            'UnicodeText': StringType(),  # Defaulting to StringType for Unicode
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
            schema_details:
            spark_df (DataFrame): Spark DataFrame.

        Returns:
            DataFrame: Spark DataFrame with matched data types.
        """
        schema_details = schema_details if schema_details else self.schema_details
        for col, dtype in schema_details.items():
            spark_dtype = self.map_to_spark_type(dtype)
            spark_df = spark_df.withColumn(
                col, spark_df[col].cast(spark_dtype))
        return spark_df

    def write_data(self, data, table_name='openetl_batches', if_exists='append', schema="public"):
        """
        Writes data to a table in etl_batches.

        Parameters:
            df (DataFrame): The DataFrame to write to the table.
            table_name (str): The name of the table to write to.
        """

        df = pd.DataFrame(data, index=[0])
        print(df)
        with self.engine.connect() as con:
            df.to_sql(
                table_name, con=con, if_exists=if_exists, index=False, schema=schema)
        return True

    def create_session(self):
        """
        Create a new session and initialize metadata and base.
        """
        Session = sessionmaker(bind=self.engine)
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

    def __dispose__(self):
        """
        Dispose the session and engine.
        """
        logging.info("DISPOSING SCHEMA UTILS SQLALCHEMY ENGINE")
        self.engine.dispose()

    def create_schema_if_not_exists(self, schema_name='open_etl'):
        """
        Creates a schema in the database if it does not already exist.

        Parameters:
            schema_name (str): The name of the schema to create. Defaults to 'open_etl'.

        Returns:
            None
        """
        with self.engine.connect() as connection:
            connection.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

    def alter_table_column_add_primary_key(self, table_name, column_name='uid', schema_name='open_etl'):
        """
        Alter a table by adding a primary key to a specified column.

        Args:
            table_name (str): The name of the table to alter.
            column_name (str): The name of the column to set as the primary key. Defaults to 'uid'.
            Currently not working changes do not reflect in the database.

        Returns:
            bool: True if the primary key addition is successful, False otherwise.
        """

        existing_table = Table(
            table_name, self.metadata, autoload_with=self.engine, schema=schema_name)

        column = existing_table.columns[column_name]
        primary_key_constraint = PrimaryKeyConstraint(column)
        existing_table.append_constraint(primary_key_constraint)
        self.metadata.create_all(self.engine)

        return True



    def create_table_from_base(self, target_schema="public",base=None):
        try:
            if not self.engine.dialect.has_schema(self.engine, "public"):
                self.engine.execute(CreateSchema(target_schema))
        except Exception as e:
            # If schema already exists, it will raise a ProgrammingError which we can ignore
            pass
        metadata = MetaData(schema=target_schema)

        # Inspect the existing table structure to check for differences
        inspector = inspect(self.engine)
        table_exists = inspector.has_table(base.__tablename__, schema=target_schema)

        if table_exists:
            model_columns = {}
            for column_name, column in base.__table__.columns.items():
                model_columns[column_name] = column.type # Convert type to string

            # Get columns from the table in the database
            inspector = inspect(self.engine)
            existing_columns = [col['name'] for col in inspector.get_columns(base.__tablename__)]

            # Identify missing columns
            missing_columns = {col: col_type for col, col_type in model_columns.items() if col not in existing_columns}

            extra_columns = [col for col in existing_columns if col not in model_columns]

            # Drop extra columns from the table
            for column_name in extra_columns:
                self.alter_table_column_add_or_drop_alembic(table_name=base.__tablename__,
                                                            column_name=column_name,
                                                            column_details=None, action=ColumnActions.DROP)

            # Add missing columns to the table
            for column_name, column_type_sql in missing_columns.items():
                self.alter_table_column_add_or_drop_alembic(table_name=base.__tablename__,
                                                            column_name=column_name,
                                                            column_details=column_type_sql, action=ColumnActions.ADD)
        else:
            # Create the table if it doesn't exist
            base.metadata.create_all(self.engine)



    def fetch_rows(self, table_name='openetl_documents', schema_name='open_etl', conditions: dict = {}):
        """
        Executes a select query on the specified table with the provided conditions.

        Args:
            table_name (str, optional): The name of the table to fetch rows from. Defaults to 'openetl_documents'.
            schema_name (str, optional): The schema of the table. Defaults to 'open_etl'.
            conditions (dict, optional): The conditions to filter the rows. Defaults to {}.

        Returns:
            ResultProxy: The result of the select query.
        """

        table = Table(table_name, self.metadata,
                      autoload_with=self.engine, schema=schema_name)
        document_column = table.columns.document
        where_condition = []

        for key, value in conditions.items():
            where_condition.append(table.columns[key] == value)

        columns = [table.columns[column_name]
                   for column_name in table.columns.keys()]
        data = ''
        result = None
        # Execute a select query with the WHERE clause
        with self.engine.connect() as connection:
            query = select(columns).where(and_(*where_condition))
            result = connection.execute(query)
        return result

    def fetch_document(self, table_name='openetl_documents', schema_name='open_etl', conditions: dict = {}):
        """
        Fetches a single document based on the specified table, schema, and conditions.

        Args:
            table_name (str, optional): The name of the table to fetch the document from. Defaults to 'openetl_documents'.
            schema_name (str, optional): The schema of the table. Defaults to 'open_etl'.
            conditions (dict, optional): The conditions to filter the document retrieval. Defaults to {}.

        Returns:
            dict: A dictionary representing the fetched document with column names as keys.
        """

        result = self.fetch_rows(
            table_name=table_name, schema_name=schema_name, conditions=conditions)
        data = result.fetchall()
        columns = result.keys()
        rows_with_column_names = [
            {column_name: row_value for column_name, row_value in zip(columns, row)} for row in data]

        return rows_with_column_names[0]

    def write_document(self, document, table_name='openetl_documents', schema_name='open_etl') -> tuple[bool, str]:
        """
        Writes a document to the specified table in the database.

        Args:
            document (dict): The document to be written. It should contain a 'document' key with the document content.
            table_name (str, optional): The name of the table to write the document to. Defaults to 'openetl_documents'.
            schema_name (str, optional): The schema of the table. Defaults to 'open_etl'.

        Returns:
            bool: True if the document is successfully written, False otherwise.

        Raises:
            Exception: If an error occurs while writing the document. The error message is logged.
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Create an instance of OpenETLDocument
        new_document = OpenETLDocument(
            connection_credentials=document['connection_credentials'],
            connection_name=document['connection_name'],
            connection_type=document['connection_type'],
            auth_type=document['auth_type'],
            connector_name=document['connector_name'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(new_document)
        session.commit()

        session.close()
        return True, ""

    def delete_document(self, document_id: int = None):
        """
        Deletes a document from the specified table in the database.

        Args:
            document_id:

        Returns:
            bool: True if the document is successfully deleted, False otherwise.

        Raises:
            Exception: If an error occurs while deleting the document. The error message is logged.
        """
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            document = session.query(OpenETLDocument).filter_by(id=document_id).first()
            integrations = (
                session.query(OpenETLIntegrations)
                .filter(or_(
                    OpenETLIntegrations.source_connection == document_id,
                    OpenETLIntegrations.target_connection == document_id
                ))
                .all()
            )
            if integrations:
                for integration in integrations:
                    session.query(OpenETLIntegrationsRuntimes).filter(
                        OpenETLIntegrationsRuntimes.integration == integration.id
                    ).delete()
                    session.delete(integration)
                    session.commit()
            if document:
                session.delete(document)
                session.commit()
                session.close()
                return True, ""
            else:
                session.close()
                raise NoResultFound(f"Document with id {document_id} not found")
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            if 'session' in locals():
                session.close()
            return False, f"Error deleting document: {e}"


    def get_created_connections(self, connector_type=None, connection_name=None, id=None) -> pd.DataFrame:
        """
        Returns a list of created connections for the specified connector type.

        Args:
            connector_type (ConnectionType): The value of type of connector, defaults to ConnectionType.DATABASE.

        Returns:
            list: A dataframe of created connections.
        """
        columns_to_fetch = [
            OpenETLDocument.connection_name,
            OpenETLDocument.connection_type,
            OpenETLDocument.auth_type,
            OpenETLDocument.connector_name,
            OpenETLDocument.connection_credentials,
            OpenETLDocument.id
        ]
        conditions = []

        if connector_type is not None:
            conditions.append(OpenETLDocument.connection_type == connector_type)
        if connection_name is not None:
            conditions.append(OpenETLDocument.connection_name == connection_name)
        if id is not None:
            conditions.append(OpenETLDocument.id == id)

        # Construct the query
        if conditions:
            select_query = select(*columns_to_fetch).where(and_(*conditions))
        else:
            select_query = select(*columns_to_fetch)

        # Execute the query and fetch data into a DataFrame
        data = pd.read_sql(select_query, self.session.bind)
        result = data.to_dict(orient='records')

        return result

    def save_oauth_token(self, access_token, refresh_token, expires_in, scope, connection_id):
        """
        Args:
            access_token:
            refresh_token:
            expires_in:
            scope:
            connection_id:
        """
        oauth_ = OpenETLOAuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            scope=scope,
            connection=connection_id
        )
        self.session.add(oauth_)
        self.session.commit()
        return True

    def get_oauth_token(self, connection_id):
        return self.session.query(OpenETLOAuthToken).filter(OpenETLOAuthToken.connection == connection_id).one_or_none()

    def delete_oauth_token(self, connection_id):
        self.session.query(OpenETLOAuthToken).filter(OpenETLOAuthToken.connection == connection_id).delete(synchronize_session=False)
        self.session.commit()
        return True


    def insert_openetl_batch(self, start_date, integration_id, batch_type, batch_status, batch_id, integration_name, rows_count=0, end_date=None, run_id=None):
        """
        Inserts a new OpenETLBatch instance into the database.

        Args:
            integration_id: The ID of the integration.
            start_date (datetime): The start date of the batch.
            batch_type (str): The type of the batch.
            batch_status (str): The status of the batch.
            batch_id (str): The unique identifier of the batch.
            integration_name (str): The name of the integration.
            rows_count (int, optional): The number of rows in the batch. Defaults to 0.
            end_date (datetime, optional): The end date of the batch. Defaults to None.
            run_id (UUID): The run ID of the batch. Defaults to None.

        Returns:
            OpenETLBatch: The newly created OpenETLBatch instance.
        """
        # Get the current highest batch_id
        def get_max_id(session, model, filters=None):
            query = select(model.id).order_by(desc(model.id)).limit(1)
            if filters:
                query = query.filter_by(**filters)
            result = session.execute(query).scalar()
            return result or 0

        session = self.session


        # Create new OpenETLBatch instance
        new_batch = OpenETLBatch(
            uid=int(get_max_id(session, OpenETLBatch) + 1),
            batch_id=batch_id,
            integration_id=integration_id,
            start_date=start_date,
            end_date=end_date,
            batch_type=batch_type,
            batch_status=batch_status,
            integration_name=integration_name,
            rows_count=rows_count,
            run_id=run_id
        )

        # Add and commit the new batch to the session
        session.add(new_batch)
        session.commit()
        return new_batch


    def update_openetl_batch(self, batch_id, integration_id, **kwargs):
        """
        Updates an OpenETLBatch object in the database with the specified batch_id.

        Args:
            batch_id (int): The ID of the batch to update.
            **kwargs: Keyword arguments specifying the fields to update and their new values.

        Returns:
            OpenETLBatch: The updated OpenETLBatch object.

        Raises:
            Exception: If no OpenETLBatch object with the specified batch_id is found.
        """
        
        session = self.session
        # Find the batch by batch_id
        batch = session.query(OpenETLBatch).filter(
            OpenETLBatch.batch_id == batch_id, OpenETLBatch.integration_id == integration_id).one_or_none()

        if batch is not None:
            for key, value in kwargs.items():
                if value is not None:
                    if key in ['rows_count']:
                        existing_value = getattr(batch, key)
                        value = existing_value + value
                    setattr(batch, key, value)

            session.commit()
            return batch
        else:
            raise NoResultFound


    def update_openetl_document(self, document_id, **kwargs):
        """
        Updates an OpenETLBatch object in the database with the specified batch_id.

        Args:
            document_id (int): The ID of the batch to update.
            **kwargs: Keyword arguments specifying the fields to update and their new values.

        Returns:
            OpenETLBatch: The updated OpenETLBatch object.

        Raises:
            Exception: If no OpenETLBatch object with the specified batch_id is found.
        """

        session = self.session
        # Find the batch by batch_id
        batch = session.query(OpenETLDocument).filter(
            OpenETLDocument.id == document_id).one_or_none()

        if batch is not None:
            # Update the specified fields
            for key, value in kwargs.items():
                if value is not None:
                    setattr(batch, key, value)
            session.commit()
            return batch
        else:
            raise NoResultFound

    def get_dashboard_data(self, page: int = 1, per_page: int = 30):
        """
        Retrieves dashboard data including total counts and paginated integration details.

        Args:
            page (int, optional): The page number for integrations. Defaults to 1.
            per_page (int, optional): The number of items per page for integrations. Defaults to 30.

        Returns:
            dict: A dictionary containing total counts and paginated integration details.
        """

        session = self.session

        # Retrieve total counts
        total_api_connections = session.query(OpenETLDocument).filter(
            OpenETLDocument.connection_type == ConnectionType.API.value).count()
        total_db_connections = session.query(OpenETLDocument).filter(
            OpenETLDocument.connection_type == ConnectionType.DATABASE.value).count()
        total_pipelines = session.query(OpenETLIntegrations).count()
        total_rows_migrated = session.query(
            func.sum(OpenETLIntegrationsRuntimes.row_count)).scalar()

        # Retrieve integration details with pagination
        offset = (page - 1) * per_page

        latest_runs_subquery = session.query(
            OpenETLIntegrationsRuntimes.integration,
            func.max(OpenETLIntegrationsRuntimes.start_date).label('latest_start_date')
        ).group_by(OpenETLIntegrationsRuntimes.integration).subquery()

        integrations_query = session.query(
            OpenETLIntegrationsRuntimes.integration,
            OpenETLIntegrationsRuntimes.run_status,
            OpenETLIntegrationsRuntimes.start_date,
            OpenETLIntegrationsRuntimes.end_date,
            OpenETLIntegrationsRuntimes.error_message
        ).join(
            latest_runs_subquery,
            (OpenETLIntegrationsRuntimes.integration == latest_runs_subquery.c.integration) &
            (OpenETLIntegrationsRuntimes.start_date == latest_runs_subquery.c.latest_start_date)
        ).order_by(
            OpenETLIntegrationsRuntimes.created_at.desc()
        ).offset(offset).limit(per_page)

        integrations = integrations_query.all()

        # Total integration count for pagination
        total_integrations = session.query(latest_runs_subquery.c.integration).count()

        # Retrieve run counts by integration
        run_counts = session.query(
            OpenETLIntegrationsRuntimes.integration,
            func.count(OpenETLIntegrationsRuntimes.id).label('run_count')
        ).group_by(OpenETLIntegrationsRuntimes.integration).all()

        run_count_dict = {run.integration: run.run_count for run in run_counts}

        integrations_dict = [
            {
                "integration_name": integration.integration,
                "latest_run_status": integration.run_status,
                "start_date": integration.start_date.isoformat() if integration.start_date else None,
                "end_date": integration.end_date.isoformat() if integration.end_date else None,
                "error_message": integration.error_message,
                "run_count": run_count_dict.get(integration.integration, 0)
            }
            for integration in integrations
        ] if integrations else []

        total_pages = (total_integrations + per_page - 1) // per_page

        # Return the dashboard data with pagination
        return {
            "page": page,
            "per_page": per_page,
            "total_items": total_integrations,
            "total_pages": total_pages,
            'total_api_connections': total_api_connections or 0,
            'total_db_connections': total_db_connections or 0,
            'total_pipelines': total_pipelines or 0,
            'total_rows_migrated': total_rows_migrated or 0,
            'integrations': {
                "data": integrations_dict
            }
        }

    def get_all_integration(self, page: int = 1, per_page: int = 30, integration_id=None):
        """
        Get all integrations paginated.

        Args:
            page (int, optional): The page number. Defaults to 1.
            per_page (int, optional): The number of items per page. Defaults to 30.

        Returns:
            dict: A dictionary containing the paginated results.
        """
        offset = (page - 1) * per_page
        schedulers = None
        total_items = 0

        if integration_id:
            schedulers = self.session.query(OpenETLIntegrations) \
                .filter(OpenETLIntegrations.id == integration_id) \
                .order_by(OpenETLIntegrations.created_at.desc())

            total_items = schedulers.count()
            schedulers = schedulers.offset(offset).limit(per_page).all()
        else:
            schedulers = self.session.query(OpenETLIntegrations) \
                .order_by(OpenETLIntegrations.created_at.desc()) \
                .offset(offset) \
                .limit(per_page)
            total_items = self.session.query(OpenETLIntegrations).count()
            schedulers = schedulers.all()

        results = [
            {
                "uid": scheduler.id,
                "integration_name": scheduler.integration_name,
                "integration_type": scheduler.integration_type,
                "cron_expression": [parse_cron_expression(cron) for cron in scheduler.cron_expression],
                "is_running": scheduler.is_running,
                "is_enabled": scheduler.is_enabled,
                "created_at": scheduler.created_at.isoformat() if scheduler.created_at else None,
                "updated_at": scheduler.updated_at.isoformat() if scheduler.updated_at else None,
            }
            for scheduler in schedulers
        ]
        total_pages = (total_items + per_page - 1) // per_page

        return {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "data": results
        }

    def get_integration_history(self, integration_id, page: int = 1, per_page: int = 30):

        offset = (page - 1) * per_page

        # Fetch the integration details
        integration = self.session.query(OpenETLIntegrations).filter_by(id=integration_id).first()

        if not integration:
            return {
                "error": f"Integration with ID {integration_id} not found."
            }

        history_query = self.session.query(OpenETLIntegrationsRuntimes) \
            .filter(OpenETLIntegrationsRuntimes.integration == integration_id) \
            .order_by(OpenETLIntegrationsRuntimes.created_at.desc())

        total_items = history_query.count()
        total_pages = (total_items + per_page - 1)

        history = history_query.offset(offset).limit(per_page).all()

        return {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "data": integration,
            "history": history
        }

    def create_integration(self, integration_name, integration_type, target_schema, source_schema, spark_config,
                           hadoop_config, cron_expression, source_connection,target_connection, source_table, target_table,
                           batch_size):
        scheduler = OpenETLIntegrations(
            integration_name=integration_name,
            integration_type=integration_type,
            cron_expression=cron_expression,
            source_connection=source_connection,
            target_connection=target_connection,
            source_table=source_table,
            target_table=target_table,
            spark_config=spark_config,
            hadoop_config=hadoop_config,
            source_schema=source_schema,
            target_schema=target_schema,
            batch_size=batch_size
        )

        self.session.add(scheduler)
        self.session.commit()
        return scheduler

    def delete_integration(self, record_id):
        self.session.query(OpenETLIntegrations).filter(OpenETLIntegrations.id == record_id).delete(synchronize_session=False)
        self.session.commit()

    def update_integration(self, record_id, **kwargs):
        batch = self.session.query(OpenETLIntegrations).filter(OpenETLIntegrations.id == record_id).first()

        if not batch:
            return NoResultFound
        for key, value in kwargs.items():
            if hasattr(batch, key):
                setattr(batch, key, value)
        self.session.commit()
        return batch

    def update_integration_runtime(self, job_id, **kwargs):
        batch = self.session.query(OpenETLIntegrationsRuntimes).filter(
            OpenETLIntegrationsRuntimes.integration == job_id,
            OpenETLIntegrationsRuntimes.celery_task_id == job_id
        ).order_by(OpenETLIntegrationsRuntimes.created_at.desc()).first()

        if not batch:
            raise NoResultFound

        for key, value in kwargs.items():
            if hasattr(batch, key):
                if key == 'row_count_trg':
                    # Add the row_count_trg value if it already exists in the database record
                    current_row_count = getattr(batch, 'row_count_trg', 0)
                    if current_row_count is None:
                        current_row_count = 0
                    setattr(batch, 'row_count_trg', current_row_count + value)
                else:
                    setattr(batch, key, value)

        self.session.commit()
        return batch

    def get_integrations_to_schedule(self) -> list[Type[OpenETLIntegrations]]:
        return self.session.query(OpenETLIntegrations).filter(
            OpenETLIntegrations.is_enabled == True,
            OpenETLIntegrations.is_running == False
        ).all()


    def create_integration_history(self, **kwargs):
        scheduler = OpenETLIntegrationsRuntimes(**kwargs)
        self.session.add(scheduler)
        self.session.commit()
        return scheduler


def get_open_etl_document_connection_details(url=False):
    """Get connection details for OpenETL Document"""

    if url:
        return "postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{database}".format(
            username=os.getenv("OPENETL_DOCUMENT_USER","rusab1"),
            password=os.getenv("OPENETL_DOCUMENT_PASS","1234"),
            hostname=os.getenv("OPENETL_DOCUMENT_HOST","localhost"),
            port=os.getenv("OPENETL_DOCUMENT_PORT","5432"),
            database=os.getenv("OPENETL_DOCUMENT_DB","airflow")
        )
    return {
        "engine": os.getenv("OPENETL_DOCUMENT_ENGINE","PostgreSQL"),
        "hostname": os.getenv("OPENETL_DOCUMENT_HOST","localhost"),
        "username": os.getenv("OPENETL_DOCUMENT_USER","rusab1"),
        "password": os.getenv("OPENETL_DOCUMENT_PASS","1234"),
        "port": os.getenv("OPENETL_DOCUMENT_PORT","5432"),
        "database": os.getenv("OPENETL_DOCUMENT_DB","airflow")
    }

def generate_cron_expression(frequency, schedule_time, schedule_dates=None):
    time_parts = schedule_time.split(':')
    minute = time_parts[1]
    hour = time_parts[0]

    if frequency.lower() == 'hourly':
        return [f"0 * * * *"]
    elif frequency.lower() == 'daily':
        return [f"{minute} {hour} * * *"]
    elif frequency.lower() == 'weekly':
        return [f"{minute} {hour} * * 0"]  # Sunday
    elif frequency.lower() == 'weekdays':
        # Monday(1) to Friday(5)
        return [f"{minute} {hour} * * 1-5"]
    elif frequency.lower() == 'weekends':
        # Saturday(6) and Sunday(0)
        return [f"{minute} {hour} * * 6,0"]
    elif schedule_dates:
        cron_expressions = []
        for date_str in schedule_dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day = date_obj.day
            month = date_obj.month
            cron_expressions.append(f"{minute} {hour} {day} {month} *")
        return cron_expressions
    else:
        raise ValueError("Unsupported scheduling details provided.")



def parse_cron_expression(cron_expr):
    """
    Parses a cron expression into its components, determines the next execution time,
    and provides a human-readable explanation.

    Args:
    - cron_expr (str): A standard 5-part cron expression.

    Returns:
    - dict: Parsed cron details and next execution time.
    """
    cron_parts = cron_expr.split()
    if len(cron_parts) != 5:
        raise ValueError("Invalid cron expression. It should have exactly 5 parts.")

    minute, hour, day_of_month, month, day_of_week = cron_parts

    def format_day_of_week(component):
        if component == "*":
            return "every day of the week"
        if component == "1-5":
            return "weekdays (Monday to Friday)"
        if component == "0,6" or component == "6,0":
            return "weekends (Saturday and Sunday)"
        if "," in component:
            days = component.split(",")
            days_map = {"0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
                        "4": "Thursday", "5": "Friday", "6": "Saturday"}
            day_names = [days_map.get(day, day) for day in days]
            return "multiple days: " + ", ".join(day_names)
        if "-" in component:
            start, end = component.split("-")
            days_map = {"0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
                        "4": "Thursday", "5": "Friday", "6": "Saturday"}
            return f"days from {days_map.get(start, start)} to {days_map.get(end, end)}"
        return f"specific day(s) of week: {component}"

    # Component formatting function
    def format_component(component, name):
        if component == "*":
            return f"Every {name}"
        elif "," in component:
            return f"Multiple {name}s: {component}"
        elif "-" in component:
            return f"Range of {name}s: {component}"
        elif "*/" in component:
            return f"Every {component[2:]} {name}s"
        return f"Specific {name}: {component}"

    # Convert cron values to detailed text
    details = {
        "minute": format_component(minute, "minute"),
        "hour": format_component(hour, "hour"),
        "day_of_month": format_component(day_of_month, "day of month"),
        "month": format_component(month, "month"),
        "day_of_week": format_day_of_week(day_of_week),
    }

    # Compute next execution using croniter (prevents infinite loops)
    now = datetime.now()
    cron = croniter(cron_expr, now)
    next_execution = cron.get_next(datetime)

    next_execution_12hr = next_execution.strftime('%I:%M %p')

    # Explanation
    explanation = (
        f"This schedule runs at {details['hour']}:{details['minute']} on {details['day_of_month']} "
        f"during {details['month']}. It happens on {details['day_of_week']}. "
        f"The next execution will be at {next_execution_12hr} on {next_execution.strftime('%B %d, %Y')}."
    )

    return {
        **details,
        "next_execution": next_execution_12hr,
        "next_execution_full": next_execution.strftime('%Y-%m-%d %I:%M %p'),
        "cron_expression": cron_expr,
        "explanation": explanation
    }
