from flask import Flask, jsonify
from flask_cors import CORS
import threading, time, json, requests
from kafka import KafkaConsumer
import base64, os
from cryptography.fernet import Fernet

# Configuration
KAFKA_BROKER = "kafka:9092"
TRAFFIC_TOPIC = "traffic-data"
CONSUMER_GROUP = "traffic-monitoring-group"
PREDICTOR_API_URL = "http://traffic_signal:5000/api/traffic"  # Adjust if needed

# Load encryption key (must match simulation.py and predictor)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("Missing ENCRYPTION_KEY environment variable")
cipher = Fernet(ENCRYPTION_KEY.encode())

app = Flask(__name__)

# History buffers (in-memory, storing up to MAX_HISTORY snapshots)
MAX_HISTORY = 100
raw_data_history = []        
prediction_history = []      

def decrypt_message(encrypted_message):
    try:
        decrypted_data = cipher.decrypt(base64.b64decode(encrypted_message))
        return json.loads(decrypted_data)
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def consume_raw_data():
    consumer = KafkaConsumer(
        TRAFFIC_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=CONSUMER_GROUP,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda v: v.decode('utf-8')
    )
    for msg in consumer:
        payload = decrypt_message(msg.value)
        if payload:
            if "timestamp" not in payload:
                payload["timestamp"] = time.time()
            raw_data_history.append(payload)
            if len(raw_data_history) > MAX_HISTORY:
                raw_data_history.pop(0)
        time.sleep(0.1)

def poll_prediction_data():
    while True:
        try:
            response = requests.get(PREDICTOR_API_URL, timeout=3)
            if response.status_code == 200:
                pred_snapshot = response.json()
                if "timestamp" not in pred_snapshot:
                    pred_snapshot["timestamp"] = time.time()
                prediction_history.append(pred_snapshot)
                if len(prediction_history) > MAX_HISTORY:
                    prediction_history.pop(0)
            else:
                print("Error fetching predictor data:", response.status_code)
        except Exception as e:
            print("Error polling predictor API:", e)
        time.sleep(3)

@app.route('/api/monitoring/', methods=['GET'])
def get_monitoring_data():
    total_vehicle_counts = []
    raw_avg_speeds = []      # weighted average speed per snapshot
    raw_densities = []       # weighted average density per snapshot
    raw_performance = []     # performance score = avg_speed * total_vehicle_count

    for snap in raw_data_history:
        summary = snap.get("summary", {})
        total_count = sum(data.get("vehicle_count", 0) for data in summary.values())
        total_vehicle_counts.append(total_count)
        total_speed = 0
        total_density = 0
        count_sum = 0
        for road, data in summary.items():
            cnt = data.get("vehicle_count", 0)
            spd = data.get("avg_speed", 0)
            dens = data.get("density", 0)
            total_speed += spd * cnt
            total_density += dens * cnt
            count_sum += cnt
        avg_speed = total_speed / count_sum if count_sum else 0
        avg_density = total_density / count_sum if count_sum else 0
        raw_avg_speeds.append(avg_speed)
        raw_densities.append(avg_density)
        raw_performance.append(avg_speed * total_count)

    max_vehicle_count = max(total_vehicle_counts) if total_vehicle_counts else 0
    avg_vehicle_count = sum(total_vehicle_counts)/len(total_vehicle_counts) if total_vehicle_counts else 0

    # Predicted metrics
    pred_avg_speeds = []
    pred_densities = []
    pred_performance = []
    for snap in prediction_history:
        roads = snap.get("roads", {})
        total_count = sum(data.get("vehicle_count", 0) for data in roads.values())
        total_speed = 0
        total_density = 0
        count_sum = 0
        for road, data in roads.items():
            cnt = data.get("vehicle_count", 0)
            spd = data.get("avg_speed", 0)
            dens = data.get("density", 0)
            total_speed += spd * cnt
            total_density += dens * cnt
            count_sum += cnt
        avg_speed = total_speed / count_sum if count_sum else 0
        avg_density = total_density / count_sum if count_sum else 0
        pred_avg_speeds.append(avg_speed)
        pred_densities.append(avg_density)
        pred_performance.append(avg_speed * total_count)

    raw_green = {}
    for snap in raw_data_history:
        raw_detail = snap.get("raw_detail", "")
        entries = raw_detail.split(',')
        for entry in entries:
            parts = entry.split()
            if len(parts) < 2:
                continue
            road = parts[0]
            tokens = parts[1:]
            green_count = sum(1 for token in tokens if token.lower() == 'g')
            if road in raw_green:
                raw_green[road][0] += green_count
                raw_green[road][1] += len(tokens)
            else:
                raw_green[road] = [green_count, len(tokens)]
    avg_green_percentage = {}
    for road, (green_total, token_total) in raw_green.items():
        avg_green_percentage[road] = (green_total / token_total * 100) if token_total else 0

    # Predicted green light distribution from prediction_history.
    predicted_green = {}
    for snap in prediction_history:
        gl = snap.get("green_light")
        if gl:
            predicted_green[gl] = predicted_green.get(gl, 0) + 1

    analytics = {
        "max_vehicle_count": max_vehicle_count,
        "avg_vehicle_count": avg_vehicle_count,
        "raw_avg_speeds": raw_avg_speeds,
        "raw_densities": raw_densities,
        "raw_performance": raw_performance,
        "pred_avg_speeds": pred_avg_speeds,
        "pred_densities": pred_densities,
        "pred_performance": pred_performance,
        "predicted_green_distribution": predicted_green,
        "avg_green_percentage": avg_green_percentage,
        "raw_history_count": len(raw_data_history),
        "prediction_history_count": len(prediction_history)
    }

    combined_data = {
        "raw_data_history": raw_data_history,
        "prediction_history": prediction_history,
        "analytics": analytics
    }
    return jsonify(combined_data)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    threading.Thread(target=consume_raw_data, daemon=True).start()
    threading.Thread(target=poll_prediction_data, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
