from kafka import KafkaConsumer
from flask import Flask, jsonify
from flask_cors import CORS
import threading, json, time, logging
import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
from datetime import datetime

app = Flask(__name__)

# Load encryption key and set up cipher
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("Missing ENCRYPTION_KEY environment variable")
cipher = Fernet(ENCRYPTION_KEY.encode())

def decrypt_message(encrypted_message):
    try:
        decrypted_data = cipher.decrypt(base64.b64decode(encrypted_message))
        return json.loads(decrypted_data)
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        return None

# Kafka configuration
KAFKA_BROKER = "kafka:9092"
NOTIFICATIONS_TOPIC = "traffic-notifications"

# Dummy authority email addresses for different event types
AUTHORITY_EMAILS = {
    "accident": "accident.authority@example.com",
    "congestion": "congestion.authority@example.com",
    "light_failure": "light.authority@example.com"
}

# In-memory store for notifications
notifications_log = []

# SMTP configuration for Gmail
GMAIL_USER = os.getenv("GMAIL_USER")
if not GMAIL_USER:
    raise ValueError("Missing GMAIL_USER environment variable")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
if not GMAIL_PASSWORD:
    raise ValueError("Missing GMAIL_PASSWORD environment variable")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email_notification(event):
    event_type = event.get("event_type", "unknown").capitalize()
    target_type = event.get("target_type", "N/A")
    target_id = event.get("target_id", "N/A")
    timestamp = event.get("timestamp", datetime.now().isoformat())
    
    # Always send the email to the authority's email address
    recipient = "naggender2@gmail.com"
    subject = f"OptiTraffic AI Alert: {event_type} Notification"
    
    # HTML email content
    html_content = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
          }}
          .container {{
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }}
          h1 {{
            color: #333333;
          }}
          p {{
            font-size: 14px;
            color: #555555;
          }}
          .details {{
            margin: 20px 0;
          }}
          .details li {{
            margin-bottom: 8px;
          }}
          .footer {{
            font-size: 12px;
            color: #888888;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>OptiTraffic AI Notification</h1>
          <p>Dear Authority,</p>
          <p>A new traffic event has been detected. Please review the details below:</p>
          <ul class="details">
            <li><strong>Event Type:</strong> {event_type}</li>
            <li><strong>Target Type:</strong> {target_type}</li>
            <li><strong>Target ID:</strong> {target_id}</li>
            <li><strong>Timestamp:</strong> {timestamp}</li>
          </ul>
          <p>Please log in to your dashboard for further details and follow-up actions.</p>
          <p>Regards,<br><strong>OptiTraffic AI Team</strong></p>
          <p class="footer">This is an automated message from the OptiTraffic AI system.</p>
        </div>
      </body>
    </html>
    """
    
    # Compose the email using MIME
    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_USER
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    # Log the notification in memory
    notifications_log.append({
        "event": event,
        "email_sent_to": recipient,
        "timestamp": timestamp
    })
    
    retries = 3
    for attempt in range(retries):
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, recipient, msg.as_string())
            server.quit()
            logging.info(f"Email successfully sent to {recipient}")
            return
        except smtplib.SMTPException as e:
            logging.error(f"Error sending email via Gmail SMTP (attempt {attempt+1}/{retries}): {e}")
            time.sleep(3)
            
def kafka_consumer_thread():
    consumer = KafkaConsumer(
        NOTIFICATIONS_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda v: decrypt_message(v.decode('utf-8'))
    )
    for msg in consumer:
        event = msg.value
        if event is None:
            continue
        logging.info(f"Received event from Kafka: {event}")
        send_email_notification(event)

threading.Thread(target=kafka_consumer_thread, daemon=True).start()

@app.route('/notifications/', methods=['GET'])
def get_notifications():
    return jsonify(notifications_log)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    app.run(host='0.0.0.0', port=5003)
