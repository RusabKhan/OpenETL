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
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.functions import lit
from pyspark.sql.types import *
from utils.cache import *
import os
import logging


class SparkConnection():

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
        self.required_libs = ["pyspark==3.5.1"]
        install_libraries(self.required_libs)

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

            # Build SparkSession
            spark_session = SparkSession.builder \
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

    def read_via_spark(self):
        """
        This method is used to read data using Spark based on the specified connection format and credentials.
        It utilizes the SparkSession and connection details to load data into a DataFrame. 
        The resulting DataFrame is stored in the sparkDataframe attribute of the SparkConnection object.
        Returns:
            pyspark.sql.DataFrame: The loaded DataFrame.

        Raises:
            Exception: If an error occurs during the data reading process.
        """

        connection_format = self.connection_string.get(
            'connection_format').lower()
        credentials = self.spark_connection_details.get(
            'spark_formatted_creds')

        try:
            sparkDataframe = self.spark_session.read.format(connection_format
                                                              ).options(**credentials
                                                                        ).load()

            self.sparkDataframe = sparkDataframe
            return sparkDataframe

        except Exception as e:
            raise Exception(str(e))

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

            return True
        except Exception as e:
            logging.error(str(e))
            return False
        
    def __dispose__(self):
        """
        Dispose the session and engine.
        """
        logging.info("DISPOSING SPARK SESSION")
        self.spark_session.stop()

