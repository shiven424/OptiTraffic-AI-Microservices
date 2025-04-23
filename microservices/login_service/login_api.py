from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import jwt
from concurrent.futures import ThreadPoolExecutor, TimeoutError

app = Flask(__name__)

# ─── JWT CONFIG ─────────────────────────────────────────────────────────────
PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH", "/etc/keys/private.pem")
JWT_ALGO         = "RS256"
JWT_EXP_SECONDS  = 3600

with open(PRIVATE_KEY_PATH, 'rb') as f:
    PRIVATE_KEY = f.read()

# ─── Simple in‑memory user store (replace with DB lookup) ────────────────────
users = {
    "1@1": "1",
    "2":   "2"
}

# ─── Executor for handling logins concurrently ──────────────────────────────
executor = ThreadPoolExecutor(max_workers=10)

def authenticate(email: str, password: str) -> dict:
    if users.get(email) == password:
        now = int(time.time())
        payload = {
            "sub": email,
            "iat": now,
            "exp": now + JWT_EXP_SECONDS
        }
        token = jwt.encode(payload, PRIVATE_KEY, algorithm=JWT_ALGO)
        return {"success": True, "access_token": token}
    else:
        return {"success": False, "message": "Invalid credentials"}

@app.route('/api/login/', methods=['POST'])
def login():
    data = request.get_json(force=True)
    email    = data.get('email', '')
    password = data.get('password', '')

    future = executor.submit(authenticate, email, password)
    try:
        # wait up to 3 seconds for auth
        result = future.result(timeout=3)
    except TimeoutError:
        return jsonify({"success": False, "message": "Authentication timeout"}), 504

    return jsonify(result)

@app.route('/oauth/token', methods=['POST'])
def oauth_token():
    return login()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True)

