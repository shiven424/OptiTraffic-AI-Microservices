FROM python:3.9-slim

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
 
# Copy microservice files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for the service
EXPOSE 8000

# Start the microservice
CMD ["python", "traffic_monitoring.py"]
