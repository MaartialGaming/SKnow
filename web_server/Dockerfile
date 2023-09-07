# Use a base image that includes Python
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and settings file to the container
COPY WebServer.py _WebServerSettings.json EditLocality.html index.html login.html requirements.txt /app/
COPY css /app/css
COPY fonts /app/fonts
COPY images /app/images
COPY js /app/js

# Make the script executable
RUN chmod +x WebServer.py

# Install required dependencies
RUN pip install -r requirements.txt

# Run the Python script when the container starts
CMD ["./WebServer.py"]
