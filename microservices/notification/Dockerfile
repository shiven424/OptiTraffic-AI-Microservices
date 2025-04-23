# Use Python base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY notification.py .
# COPY config.json .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Flask
EXPOSE 5003

# Command to run the application
CMD ["python", "notification.py"]
