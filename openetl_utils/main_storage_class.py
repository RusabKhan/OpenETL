import os
from abc import ABC, abstractmethod

from openetl_utils import install_libraries
from openetl_utils.enums import ConnectionType, AuthType


class Storage(ABC):
    """
    Abstract base class for all storage-type connectors such as S3, Azure Blob, GCS, FTP, and Local filesystem.

    This class defines the standard interface and lifecycle for handling file-based data sources or destinations.
    Each concrete storage connector must implement the defined abstract methods based on its SDK or protocol.

    Key Concepts:
    - Folders with same-type files and no nested directories are treated as 'tables'.
    - Schema inference is based on file structure within such valid folders.
    - This class supports installing required libraries dynamically and provides placeholders for basic metadata.

    Attributes:
        connection_type (ConnectionType): Type of connector (set to STORAGE).
        required_libs (list): List of required Python libraries for the connector.
        logo (str): URL to connector logo.
        engine (str): Type of storage engine (e.g., S3, Azure Blob).
        authentication_details (dict): Authentication structure using AuthType as key.
    """

    def __init__(self):
        self.connection_type = ConnectionType.STORAGE
        self.required_libs = []
        self.logo = ""
        self.engine = "Storage"

    def install_missing_libraries(self) -> bool:
        if len(self.required_libs) > 0:
            return install_libraries(self.required_libs)

    @abstractmethod
    def create_engine(self, **auth_params):
        """
        Alias for connect(). For compatibility with DB connectors.
        """
        pass

    @abstractmethod
    def connect(self, **auth_params):
        """
        Establishes a connection to the storage backend.
        """
        pass

    @abstractmethod
    def test_connection(self):
        """
        Tests if the connector can successfully access the storage.
        """
        pass

    @abstractmethod
    def list_files(self, prefix=None, **kwargs):
        """
        Lists all files under a given folder or prefix.
        """
        pass

    @abstractmethod
    def read_file(self, file_path, **kwargs):
        """
        Reads and returns the content of a file from the storage.
        """
        pass

    @abstractmethod
    def write_file(self, file_path, data, **kwargs):
        """
        Writes data to a specific file path in the storage.
        """
        pass

    @abstractmethod
    def delete_file(self, file_path, **kwargs):
        """
        Deletes a file from the storage.
        """
        pass

    @abstractmethod
    def validate_folder_structure(self, folder_path, **kwargs) -> bool:
        """
        Validates if a folder qualifies as a 'table'.
        """
        pass

    @abstractmethod
    def get_table_schema(self, folder_path, sample_size=10, **kwargs) -> dict:
        """
        Infers the schema of a folder treated as a 'table'.
        """
        pass

    @abstractmethod
    def get_metadata(self, *args, **kwargs):
        """
        Returns metadata about the storage connector.
        """
        pass

    @abstractmethod
    def read_table(self, table_name, schema_name="public", page_size=10000):
        """
        Reads a 'table' (folder of files) from storage.
        """
        pass

    @abstractmethod
    def write_data(self, data, table_name, if_exists='append', schema="public"):
        """
        Writes data to storage as a 'table'.
        """
        pass

    @abstractmethod
    def execute_query(self, query):
        """
        Not applicable for storage. Dummy method for interface compatibility.
        """
        pass

    @abstractmethod
    def close_session(self):
        """
        Closes connection/session if needed.
        """
        pass

    @abstractmethod
    def get_table_file_type(self, folder_path):
        """
        Detects the file type used in a given S3 folder (table).
        Assumes all files are of the same type.

        Args:
            folder_path (str): S3 prefix/folder path.

        Returns:
            str: File extension (e.g., '.csv', '.parquet'), or None if not identifiable.
        """
        pass