# Use a slim version of Python 3.11 as the base image
FROM python:3.11-slim

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
