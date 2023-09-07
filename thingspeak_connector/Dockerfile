# Use a base image that includes Python
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and settings file to the container
COPY ThingspeakConnector.py _ThingspeakConnectorSettings.json requirements.txt /app/

# Make the script executable
RUN chmod +x ThingspeakConnector.py

# Install required dependencies
RUN pip install -r requirements.txt

# Run the Python script when the container starts
CMD ["./ThingspeakConnector.py"]

