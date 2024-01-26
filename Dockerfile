# Use the official Python base image with Python 3.x
FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the current directory to the container
COPY . .

# Expose the port Streamlit runs on (default is 8501)
EXPOSE 8500

# Command to run the Streamlit app within the container
CMD ["streamlit", "run", "main.py"]
