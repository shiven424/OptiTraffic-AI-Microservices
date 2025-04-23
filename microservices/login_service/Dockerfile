FROM python:3.9-slim

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
 
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001
CMD ["python", "login_api.py"]
