from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.functions import lit
from pyspark.sql.types import *

SPARK_UTILITIES = {
    'snowflake': {
        'connection' :{
            "hostname": "sfUrl",
            "username": "sfUser",
            "account": "sfAccount",
            "password": "sfPassword",
            "database": "sfDatabase",
            "schema": "sfSchema",
            "warehouse": "sfWarehouse",
            "role": "sfRole",
            "table": "dbtable"
            },
        "jars":"net.snowflake:spark-snowflake_2.12:2.8.4-spark_3.0"
        },
    
    "postgresql":{
        "connection":{
            "hostname": "hostname",
            "username": "user",
            "password": "password",
            "database": "database",
            "schema": "schema",
            "port": "port",
            "classname": "driver",
            "table": "dbtable",
            "query":"query",
            "url": "url"
        },
        "pattern":"jdbc:postgresql://hostname:port/database",
        "jars":"org.postgresql:postgresql:42.5.0"
    }
}

class SparkConnection():
    
    def __init__(self,connection_credentials:dict,
                 spark_configuration:dict,
                 hadoop_configuration:dict = None,
                 sparkDataframe:pyspark.sql.DataFrame = None):
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
        self.connection_credentials = connection_credentials
        self.master = spark_configuration.get("master")
        self.applicationName = spark_configuration.get("applicationName")
        self.config = spark_configuration.get("applicationName")
        self.sparkConnection = None
        self.sparkDataframe = sparkDataframe
        self.hadoop_configuration = hadoop_configuration
        self.spark_connection_details = self.__credentials_formatter()

        
    def initializeSpark(self):
        """
        Initializes a Spark connection and configures the Spark session based on the connection and configuration details.

        Returns:
            pyspark.sql.SparkSession: The initialized SparkSession object.

        Raises:
            Exception: If an error occurs during Spark initialization.
        """
        SparkConfig = SparkConf()
        SparkConfig['spark.jars.packages'] = self.spark_connection_details['jars']
        
        try:
            for (name, value) in self.config.items():
                SparkConfig.set(name, value)
            
            sparkConnection = SparkSession.builder.master(master
                        ).appName(applicationName
                                ).config(conf=SparkConfig).getOrCreate()
                        
            
            if self.hadoop_configuration:
                sparkConn = sparkConnection.sparkContext._jsc.hadoopConfiguration()
                for (name, value) in self.hadoop_configuration.items():
                    sparkConn.set(name, value)
                    
            self.sparkConnection = sparkConnection

            return sparkConnection

        except Exception as e:
            raise Exception(str(e))
    
    
    def __credentials_formatter(self):
        """
        The credentials_formatter method is used to format the connection credentials based on the specified connection format.
        It creates a dictionary of formatted credentials suitable for establishing a Spark connection.

        Returns:
            dict: A dictionary containing the formatted credentials and additional information.

        Example:
            {
                'spark_formatted_creds': {
                    'url': 'connection_url',
                    'username': 'connection_username',
                    'password': 'connection_password'
                },
                'jars': "jar1"
            }
        """
        formated_creds = dict()
        spark_formatted_creds = dict()

        connection_format = self.connection_credentials.get(
                            'connection_format').lower()

        spark_connection = SPARK_UTILITIES[connection_format]
        
        for key,value in self.connection_credentials.items():
            if key in spark_connection['connection']:
                spark_formatted_creds[spark_connection['connection'][key]] = self.connection_credentials[key]
        
        if spark_connection.get('pattern'):
            connection_string = spark_connection['pattern']
            
            for key,value in spark_formatted_creds.items():
                connection_string = connection_string.replace(key,value)
            spark_formatted_creds['url'] = connection_string
        formated_creds['spark_formatted_creds'] = spark_formatted_creds
        formated_creds['jars'] = spark_connection['jars']
        
        return formated_creds
    
    
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
        
        connection_format = self.connection_credentials.get(
                            'connection_format').lower()
        credentials = self.spark_connection_details.get('spark_formatted_creds')
        
        try:
            sparkDataframe = self.sparkConnection.read.format(connection_format
                                    ).options(**credentials
                                            ).load()
                                
            self.sparkDataframe = sparkDataframe
            return sparkDataframe
        
        except Exception as e:
            raise Exception(str(e))
    
    
    def write_via_spark(self):
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
        connection_format = self.connection_credentials.get(
                            'connection_format').lower()
        credentials = self.spark_connection_details.get('spark_formatted_creds')
        try:
            self.sparkDataframe.write.format(connection_type).options(**connection_dict).mode(mode).save()
        except Exception as e:
            raise Exception(str(e))
            