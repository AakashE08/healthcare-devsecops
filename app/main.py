import os
import logging
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, abort
from functools import wraps

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
API_TOKEN  = os.environ.get("API_TOKEN", "")
PATIENTS   = {}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-API-Token", "")
        if not token or token != API_TOKEN:
            abort(401)
        return f(*args, **kwargs)
    return decorated

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "healthcare-api",
                    "timestamp": datetime.utcnow().isoformat()})

@app.route("/api/patients", methods=["POST"])
@require_auth
def create_patient():
    data = request.get_json()
    if not data or "name" not in data or "dob" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    patient_id = hashlib.sha256(
        f"{data['name']}{data['dob']}".encode()).hexdigest()[:12]
    PATIENTS[patient_id] = {
        "id": patient_id,
        "name": data["name"],
        "dob": data["dob"],
        "blood_type": data.get("blood_type", "Unknown"),
        "created_at": datetime.utcnow().isoformat()
    }
    return jsonify({"patient_id": patient_id, "status": "created"}), 201

@app.route("/api/patients/<patient_id>", methods=["GET"])
@require_auth
def get_patient(patient_id):
    patient = PATIENTS.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient)

@app.route("/api/patients", methods=["GET"])
@require_auth
def list_patients():
    return jsonify({"patients": list(PATIENTS.keys()), "count": len(PATIENTS)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
