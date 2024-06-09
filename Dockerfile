# Use a slim version of Python 3.11 as the base image
FROM python:3.11-slim-bullseye

# Set up dependencies for Spark and Java
RUN apt-get update \
    && apt-get install -y wget \
    && apt-get install -y openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set up Spark
ENV SPARK_VERSION=3.4.3
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark

# Download and extract Spark binary distribution
RUN wget -qO- "https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | tar xz -C /opt \
    && mv "/opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" /opt/spark \
    && echo "export SPARK_HOME=/opt/spark" >> ~/.bashrc \
    && echo "export PATH=\$PATH:\$SPARK_HOME/bin" >> ~/.bashrc

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Apache Airflow
RUN pip install apache-airflow

# Set environment variables for Airflow and OpenETL
ENV AIRFLOW_HOME=/opt/airflow \
    OPENETL_HOME=/app \
    OPENETL_DOCUMENT_HOST=postgresql \
    OPENETL_DOCUMENT_PORT=5432 \
    OPENETL_DOCUMENT_USER=airflow \
    OPENETL_DOCUMENT_PASS=airflow \
    OPENETL_DOCUMENT_DB=airflow \
    OPENETL_DOCUMENT_ENGINE=PostgreSQL

# Create the Airflow home directory
RUN mkdir -p $AIRFLOW_HOME

# Copy the entire content of the current directory to /app in the container
COPY . .

# Move the Airflow configuration file to the Airflow home directory
RUN mv /app/airflow.cfg $AIRFLOW_HOME/

# Expose ports for Streamlit and Airflow
EXPOSE 8500 8080
