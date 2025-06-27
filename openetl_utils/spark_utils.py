"""
This module contains utility functions and classes for working with Apache Spark.

Classes:
- SparkConnection: Represents a connection to a Spark cluster.

Functions:
- initializeSpark: Initializes a Spark connection and configures the Spark session based on the connection and configuration details.
- read_via_spark: Reads data using Spark based on the specified connection format and credentials.
- other_function_name(): Description of what this function does.
- another_function_name(): Description of what this function does.
"""
import uuid

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
import os

import logging
class SparkConnection():
    
    """
    A class representing a connection to a Spark cluster.

    Attributes:
         (str): The connection string for the Spark cluster.
        spark_configuration (dict): Dictionary containing Spark configuration details.
        hadoop_configuration (dict, optional): Dictionary containing Hadoop configuration details.
        jar (None): Placeholder for the JAR file.

    Methods:
        initializeSpark(): Initializes a Spark connection and configures the Spark session.
        read_via_spark(): Reads data using Spark based on the specified connection format and credentials.
        write_via_spark(dataframe, conn_string, table, driver, mode="append", format="jdbc"): Writes data using Spark.
        __dispose__(): Disposes the Spark session and engine.
    """

    def __init__(self, connection_string: str,
                 spark_configuration: dict,
                 hadoop_configuration: dict = None,
                 jar=None):
        """
        Initializes a SparkConnection object with the provided connection and configuration details.

        Args:
            connection_credentials (dict): A dictionary containing the credentials required for establishing the connection.
            spark_configuration (dict): A dictionary containing the Spark configuration details.
                It should contain the following keys:
                - 'master': The URL of the Spark master.
                - 'applicationName': The name of the Spark application.
            hadoop_configuration (dict, optional): A dictionary containing the Hadoop configuration details.
                Defaults to None.
            sparkDataframe (pyspark.sql.DataFrame, optional): An optional Spark DataFrame to associate with the SparkConnection.
                Defaults to None.

        Attributes:
            connection_credentials (dict): The credentials required for establishing the connection.
            master (str): The URL of the Spark master.
            applicationName (str): The name of the Spark application.
            config (str): The name of the Spark application (same as applicationName).
            sparkConnection (None): A placeholder for the Spark connection object.
            sparkDataframe (pyspark.sql.DataFrame): The associated Spark DataFrame, if provided.
            hadoop_configuration (dict): The Hadoop configuration details, if provided.
            spark_connection_details (str): A formatted string containing the connection details.

        Returns:
            None
        """
        os.environ['SPARK_LOCAL_IP'] = "localhost"

        self.connection_string = connection_string
        self.spark_configuration = spark_configuration
        self.hadoop_configuration = hadoop_configuration
        self.jar = jar

    def initializeSpark(self) -> SparkSession:
        """
        Initializes a Spark connection and configures the Spark session based on the connection and configuration details.

        Returns:
            pyspark.sql.SparkSession: The initialized SparkSession object.

        Raises:
            Exception: If an error occurs during Spark initialization.
        """
        spark_conf = SparkConf()
        spark_conf.set("spark.jars.packages", self.jar)

        # Set Spark configurations
        try:
            for name, value in self.spark_configuration.items():
                spark_conf.set(name, value)

            app_name = self.spark_configuration.get("spark.app.name", "default") + f"_{uuid.uuid4()}"

            # Build SparkSession
            spark_session = SparkSession.builder \
            .master(os.getenv("SPARK_MASTER" , "local[*]")) \
            .appName(app_name) \
            .config(conf=spark_conf) \
            .getOrCreate()

            # Set Hadoop configurations
            if self.hadoop_configuration:
                hadoop_conf = spark_session.sparkContext._jsc.hadoopConfiguration()
                for name, value in self.hadoop_configuration.items():
                    hadoop_conf.set(name, value)

            self.spark_session = spark_session
            return spark_session

        except Exception as e:
            raise Exception(str(e))

    def read_via_spark(self, spark_connection_details, source_format="jdbc", batch_size=10000):
        """
        Reads data from a Spark DataFrame using limit/offset pagination, yielding batches of data until all rows are read.
        Stops if all rows in a batch are null.

        Args:
            spark_connection_details (dict): The connection details.
            source_format (str): The source format (e.g., "jdbc").
            batch_size (int): The number of rows per batch.

        Yields:
            pyspark.sql.DataFrame: A Spark DataFrame containing a batch of rows.

        Raises:
            Exception: If an error occurs during the data reading process.
        """
        start = 0
        while True:
            # Create the pagination filter with row_number and limit/offset
            paginated_df = self.spark_session.read.format(source_format).options(**spark_connection_details).load() \
                .withColumn("row_number", F.row_number().over(Window.orderBy(F.lit(1)))) \
                .filter((F.col("row_number") > start) & (F.col("row_number") <= start + batch_size)) \
                .drop("row_number")

            if paginated_df.count() == 0:
                break

            yield paginated_df

            start += batch_size

    def write_via_spark(self, dataframe, conn_string, table,driver, mode="append",format="jdbc"):
        """
        The write_via_spark method is used to write data using Spark based on the specified connection format and credentials. 
        It takes the DataFrame stored in the sparkDataframe attribute of the SparkConnection object and writes it to the target data destination.

        The method requires a valid connection format and corresponding credentials to establish the connection for writing data. 
        It uses the write method of the DataFrame API, specifying the connection format, options, and save mode.

        If any error occurs during the data writing process, an exception is raised.

        This method is typically used after establishing a Spark connection, configuring the connection format and credentials, and preparing the data in the sparkDataframe attribute.

        Please note that in the provided code snippet, the variables connection_type, connection_dict, and mode are not defined. 
        Make sure to replace them with the appropriate values based on your implementation.

        Raises:
            Exception: If an error occurs during the data writing process.
        """
        try:
            dataframe.write \
                .format(format) \
                .option("url", conn_string) \
                .option("dbtable", table) \
                .option("driver", driver) \
                .mode(mode) \
                .save()

            return True, "Data written successfully"
        except Exception as e:
            logging.error(str(e))
            return False, str(e)
        
    def __dispose__(self):
        """
        Dispose the session and engine.
        """
        logging.info("DISPOSING SPARK SESSION")
        self.spark_session.stop()

