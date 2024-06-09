# Use a slim version of Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire content of the current directory to /app in the container
COPY . .

# Expose port 8500 for Streamlit
EXPOSE 8500

# Define the command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]
