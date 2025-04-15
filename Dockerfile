# Use a base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application code into the Docker image
COPY . /app

# Install system dependencies required for mysqlclient and npm before Python dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    npm \
    && apt-get clean

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN npm install

# Set the entry point to run the application
CMD ["python", "app.py"]
