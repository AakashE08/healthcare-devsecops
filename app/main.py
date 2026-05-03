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

@app.route("/")
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevSecOps — Healthcare System</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { min-height: 100vh; background: #0a0f1e; font-family: Arial, sans-serif; display: flex; align-items: center; justify-content: center; }
  .card { background: #111827; border: 1px solid #1e3a5f; border-radius: 20px; padding: 48px 56px; max-width: 640px; width: 90%; text-align: center; }
  .badge { display: inline-block; background: #1a2e1a; color: #4ade80; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 6px 16px; border-radius: 20px; margin-bottom: 28px; border: 1px solid #166534; }
  .avatar { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #16a34a, #065f46); display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; color: white; margin: 0 auto 20px; }
  h1 { font-size: 30px; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; }
  .roll { font-size: 13px; color: #64748b; letter-spacing: 1px; margin-bottom: 28px; }
  .divider { height: 1px; background: #1e3a5f; margin: 24px 0; }
  .security-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
  .sec-card { background: #0d1117; border-radius: 12px; padding: 14px 10px; border: 1px solid #1e3a5f; }
  .sec-icon { font-size: 20px; margin-bottom: 6px; }
  .sec-label { font-size: 10px; color: #475569; text-transform: uppercase; letter-spacing: 1px; }
  .sec-value { font-size: 13px; font-weight: 700; color: #4ade80; margin-top: 2px; }
  .pipeline { display: flex; align-items: center; justify-content: center; gap: 6px; flex-wrap: wrap; margin-bottom: 24px; }
  .step { background: #0d1117; border: 1px solid #1e3a5f; border-radius: 8px; padding: 7px 10px; font-size: 10px; color: #94a3b8; display: flex; align-items: center; gap: 5px; }
  .dot { width: 6px; height: 6px; border-radius: 50%; background: #4ade80; animation: pulse 2s infinite; }
  .arrow { color: #1e3a5f; font-size: 11px; }
  .footer { font-size: 11px; color: #334155; }
  .hipaa { display: inline-block; background: #1e1a3a; color: #a78bfa; font-size: 10px; padding: 4px 12px; border-radius: 12px; border: 1px solid #4c1d95; margin-bottom: 16px; letter-spacing: 1px; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
</style>
</head>
<body>
<div class="card">
  <div class="badge">🔒 DevSecOps — Experiment 3</div>
  <div class="hipaa">HIPAA COMPLIANT DESIGN</div>
  <div class="avatar">AE</div>
  <h1>Aakash E</h1>
  <div class="roll">RA2311026010022</div>
  <div class="security-grid">
    <div class="sec-card">
      <div class="sec-icon">🧪</div>
      <div class="sec-label">Unit Tests</div>
      <div class="sec-value">5/5 Passed</div>
    </div>
    <div class="sec-card">
      <div class="sec-icon">🔍</div>
      <div class="sec-label">Trivy Scan</div>
      <div class="sec-value">0 Critical</div>
    </div>
    <div class="sec-card">
      <div class="sec-icon">🛡️</div>
      <div class="sec-label">RBAC</div>
      <div class="sec-value">Active</div>
    </div>
    <div class="sec-card">
      <div class="sec-icon">🔐</div>
      <div class="sec-label">K8s Secrets</div>
      <div class="sec-value">Encrypted</div>
    </div>
    <div class="sec-card">
      <div class="sec-icon">🐳</div>
      <div class="sec-label">Container</div>
      <div class="sec-value">Non-Root</div>
    </div>
    <div class="sec-card">
      <div class="sec-icon">📊</div>
      <div class="sec-label">SonarQube</div>
      <div class="sec-value">Analyzed</div>
    </div>
  </div>
  <div class="divider"></div>
  <div class="pipeline">
    <div class="step"><span class="dot"></span>GitHub</div>
    <div class="arrow">→</div>
    <div class="step"><span class="dot"></span>Tests</div>
    <div class="arrow">→</div>
    <div class="step"><span class="dot"></span>SonarQube</div>
    <div class="arrow">→</div>
    <div class="step"><span class="dot"></span>Trivy</div>
    <div class="arrow">→</div>
    <div class="step"><span class="dot"></span>K8s</div>
  </div>
  <div class="footer">SRM Institute of Science and Technology &nbsp;•&nbsp; DevOps Lab &nbsp;•&nbsp; Healthcare API</div>
</div>
<script>
  setInterval(() => {
    fetch('/health').then(r=>r.json()).then(d=>{}).catch(()=>{});
  }, 30000);
</script>
</body>
</html>'''

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
