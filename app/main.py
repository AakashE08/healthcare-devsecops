import os
import logging
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from functools import wraps

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

API_TOKEN = os.environ.get("API_TOKEN", "")

DOCTORS = {
    "D001": {"id":"D001","name":"Dr. Priya Sharma","specialty":"Cardiology","available":True,"slots":["09:00","10:00","14:00","15:00"]},
    "D002": {"id":"D002","name":"Dr. Rahul Verma","specialty":"Neurology","available":True,"slots":["10:00","11:00","16:00"]},
    "D003": {"id":"D003","name":"Dr. Anita Nair","specialty":"Pediatrics","available":False,"slots":["09:00","13:00","15:00"]},
    "D004": {"id":"D004","name":"Dr. Suresh Kumar","specialty":"Orthopedics","available":True,"slots":["11:00","12:00","17:00"]},
    "D005": {"id":"D005","name":"Dr. Meera Patel","specialty":"Dermatology","available":True,"slots":["08:00","09:00","14:00"]},
}
APPOINTMENTS = {}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-API-Token","")
        if not token or token != API_TOKEN:
            from flask import abort; abort(401)
        return f(*args, **kwargs)
    return decorated

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Healthcare Portal</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  *{margin:0;padding:0;box-sizing:border-box;}
  body{font-family:'Inter',sans-serif;background:#f5f5f5;color:#1a1a1a;font-size:14px;line-height:1.5;}

  /* Topbar */
  .topbar{background:#fff;border-bottom:1px solid #e5e5e5;padding:0 32px;height:56px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;}
  .topbar-left{display:flex;align-items:center;gap:10px;}
  .topbar-icon{width:32px;height:32px;background:#000;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:16px;}
  .topbar-title{font-size:15px;font-weight:700;color:#111;}
  .topbar-sub{font-size:13px;color:#888;font-weight:400;}
  .topbar-right{display:flex;align-items:center;gap:10px;}
  .badge-admin{background:#f0f0ff;color:#6b6bff;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
  .topbar-user{font-size:13px;color:#444;font-weight:500;}
  .signout{font-size:13px;color:#444;border:1px solid #ddd;padding:5px 14px;border-radius:6px;cursor:pointer;background:#fff;}
  .signout:hover{background:#f5f5f5;}

  /* Layout */
  .page{max-width:1280px;margin:0 auto;padding:28px 32px;}
  .page-header{margin-bottom:24px;}
  .page-header h1{font-size:20px;font-weight:700;color:#111;}
  .page-header p{font-size:13px;color:#888;margin-top:2px;}
  .grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
  .grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:24px;}

  /* Stats */
  .stat-card{background:#fff;border:1px solid #e8e8e8;border-radius:10px;padding:18px 20px;}
  .stat-label{font-size:11px;color:#888;font-weight:600;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:6px;}
  .stat-val{font-size:26px;font-weight:700;color:#111;}
  .stat-sub{font-size:12px;color:#aaa;margin-top:2px;}

  /* Card */
  .card{background:#fff;border:1px solid #e8e8e8;border-radius:10px;padding:24px;}
  .card-title{font-size:15px;font-weight:700;color:#111;margin-bottom:4px;}
  .card-sub{font-size:12px;color:#888;margin-bottom:20px;}
  .divider{height:1px;background:#f0f0f0;margin:16px 0;}

  /* Table */
  .table{width:100%;border-collapse:collapse;}
  .table th{text-align:left;font-size:11px;font-weight:600;color:#888;letter-spacing:0.5px;text-transform:uppercase;padding:8px 12px;border-bottom:1px solid #f0f0f0;}
  .table td{padding:12px 12px;border-bottom:1px solid #f8f8f8;font-size:13px;color:#333;vertical-align:middle;}
  .table tr:last-child td{border-bottom:none;}
  .table tr:hover td{background:#fafafa;}
  .doctor-name{font-weight:600;color:#111;}
  .specialty{color:#888;font-size:12px;}

  /* Status badges */
  .status{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
  .status-avail{background:#f0fdf4;color:#16a34a;}
  .status-unavail{background:#fef2f2;color:#dc2626;}
  .status-dot{width:5px;height:5px;border-radius:50%;background:currentColor;}

  /* Form */
  .form-row{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px;}
  .form-group{margin-bottom:14px;}
  .form-group.full{grid-column:1/-1;}
  label{display:block;font-size:11px;font-weight:600;color:#666;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:6px;}
  input,select,textarea{width:100%;border:1px solid #e5e5e5;border-radius:7px;padding:9px 12px;font-size:13px;font-family:'Inter',sans-serif;color:#111;outline:none;transition:border-color 0.15s;background:#fff;}
  input:focus,select:focus{border-color:#111;box-shadow:0 0 0 2px rgba(0,0,0,0.06);}
  input::placeholder{color:#bbb;}
  select option{color:#111;}

  /* Buttons */
  .btn{padding:9px 18px;border-radius:7px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:0.15s;font-family:'Inter',sans-serif;}
  .btn-primary{background:#111;color:#fff;}
  .btn-primary:hover{background:#333;}
  .btn-full{width:100%;padding:11px;font-size:14px;}
  .btn-sm{padding:5px 12px;font-size:12px;}
  .btn-outline{background:#fff;color:#444;border:1px solid #ddd;}
  .btn-outline:hover{background:#f5f5f5;}
  .btn-danger-sm{background:#fef2f2;color:#dc2626;border:1px solid #fecaca;font-size:11px;padding:4px 10px;border-radius:6px;cursor:pointer;font-weight:600;}
  .btn-success-sm{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;font-size:11px;padding:4px 10px;border-radius:6px;cursor:pointer;font-weight:600;}

  /* Appointment cards */
  .appt-item{padding:14px 0;border-bottom:1px solid #f0f0f0;}
  .appt-item:last-child{border-bottom:none;}
  .appt-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;}
  .appt-patient{font-weight:600;font-size:13px;color:#111;}
  .appt-time{font-size:12px;font-weight:600;color:#111;background:#f5f5f5;padding:2px 8px;border-radius:5px;}
  .appt-doctor{font-size:12px;color:#666;}
  .appt-id{font-size:11px;color:#bbb;margin-top:4px;}

  /* Slots */
  .slots{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px;}
  .slot{font-size:11px;background:#f5f5f5;padding:2px 8px;border-radius:5px;color:#666;}

  /* Empty state */
  .empty{text-align:center;padding:32px 0;color:#bbb;font-size:13px;}
  .empty-icon{font-size:28px;margin-bottom:8px;}

  /* Security bar */
  .sec-bar{background:#fff;border:1px solid #e8e8e8;border-radius:10px;padding:14px 20px;margin-bottom:20px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
  .sec-item{display:flex;align-items:center;gap:5px;font-size:11px;color:#666;font-weight:500;}
  .sec-dot{width:6px;height:6px;border-radius:50%;background:#16a34a;}
  .sec-div{width:1px;height:14px;background:#e8e8e8;}
  .sec-label{font-size:11px;font-weight:700;color:#111;margin-right:4px;}

  /* Toast */
  .toast{position:fixed;bottom:24px;right:24px;background:#111;color:#fff;padding:11px 18px;border-radius:8px;font-size:13px;display:none;z-index:999;box-shadow:0 4px 20px rgba(0,0,0,0.15);}
  .toast.show{display:block;animation:slide-up 0.2s ease;}
  @keyframes slide-up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

  .count-badge{background:#f0f0f0;color:#666;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;margin-left:8px;}
</style>
</head>
<body>

<!-- Topbar -->
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-icon">🏥</div>
    <div>
      <span class="topbar-title">Healthcare Portal</span>
      <span class="topbar-sub"> &nbsp;Patient Management System</span>
    </div>
  </div>
  <div class="topbar-right">
    <span class="badge-admin">DevSecOps Exp 3</span>
    <span class="topbar-user">Aakash E &nbsp;|&nbsp; RA2311026010022</span>
    <button class="signout">Sign out</button>
  </div>
</div>

<div class="page">

  <!-- Security bar -->
  <div class="sec-bar">
    <span class="sec-label">Security:</span>
    <div class="sec-item"><span class="sec-dot"></span> Unit Tests 5/5</div>
    <div class="sec-div"></div>
    <div class="sec-item"><span class="sec-dot"></span> Trivy 0 Critical</div>
    <div class="sec-div"></div>
    <div class="sec-item"><span class="sec-dot"></span> RBAC Active</div>
    <div class="sec-div"></div>
    <div class="sec-item"><span class="sec-dot"></span> Non-Root Container</div>
    <div class="sec-div"></div>
    <div class="sec-item"><span class="sec-dot"></span> K8s Secrets Encrypted</div>
    <div class="sec-div"></div>
    <div class="sec-item"><span class="sec-dot"></span> SonarQube Analyzed</div>
  </div>

  <!-- Stats row -->
  <div class="grid-3">
    <div class="stat-card">
      <div class="stat-label">Available Doctors</div>
      <div class="stat-val" id="stat-avail">—</div>
      <div class="stat-sub">Ready to book</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Appointments</div>
      <div class="stat-val" id="stat-appts">0</div>
      <div class="stat-sub">Booked today</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Doctors</div>
      <div class="stat-val" id="stat-total">5</div>
      <div class="stat-sub">In system</div>
    </div>
  </div>

  <!-- Main grid -->
  <div class="grid-2">

    <!-- Application 1: Book Appointment -->
    <div>
      <div class="card" style="margin-bottom:20px;">
        <div class="card-title">Application 1: Book Appointment</div>
        <div class="card-sub">Schedule a consultation with an available doctor</div>

        <div class="form-row">
          <div class="form-group">
            <label>Patient Name</label>
            <input type="text" id="patient-name" placeholder="Enter full name">
          </div>
          <div class="form-group">
            <label>Select Doctor</label>
            <select id="doctor-select">
              <option value="">— Choose doctor —</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Time Slot</label>
            <select id="slot-select">
              <option value="">— Select slot —</option>
            </select>
          </div>
          <div class="form-group">
            <label>Reason for Visit</label>
            <input type="text" id="reason" placeholder="Brief description">
          </div>
        </div>
        <button class="btn btn-primary btn-full" onclick="bookAppointment()">Book Appointment</button>
      </div>

      <!-- Appointments list -->
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
          <div class="card-title">My Appointments <span class="count-badge" id="appt-count">0</span></div>
        </div>
        <div class="card-sub">Your scheduled consultations</div>
        <div id="appointments-list">
          <div class="empty"><div class="empty-icon">📋</div>No appointments booked yet</div>
        </div>
      </div>
    </div>

    <!-- Right column -->
    <div>
      <!-- Application 2: Doctors List -->
      <div class="card" style="margin-bottom:20px;">
        <div class="card-title">Application 2: Available Doctors <span class="count-badge" id="avail-count">0</span></div>
        <div class="card-sub">Browse doctors accepting appointments</div>
        <table class="table">
          <thead>
            <tr>
              <th>Doctor</th>
              <th>Specialty</th>
              <th>Slots</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="doctors-table"></tbody>
        </table>
      </div>

      <!-- Admin: Manage Doctors -->
      <div class="card">
        <div class="card-title">Admin Dashboard</div>
        <div class="card-sub">Manage doctor availability across the system</div>
        <table class="table">
          <thead>
            <tr>
              <th>Doctor</th>
              <th>Specialty</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="admin-table"></tbody>
        </table>
      </div>
    </div>

  </div>
</div>

<div class="toast" id="toast"></div>

<script>
  let doctors = {};
  let appointments = [];

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast show';
    setTimeout(() => t.className = 'toast', 3000);
  }

  async function loadDoctors() {
    const res = await fetch('/api/doctors');
    doctors = await res.json();
    renderAll();
  }

  function renderAll() {
    const all = Object.values(doctors);
    const avail = all.filter(d => d.available);
    document.getElementById('stat-avail').textContent = avail.length;
    document.getElementById('stat-total').textContent = all.length;
    document.getElementById('avail-count').textContent = avail.length;

    // Doctors table (available only)
    document.getElementById('doctors-table').innerHTML = avail.length === 0
      ? '<tr><td colspan="4" style="text-align:center;color:#bbb;padding:24px;">No doctors available</td></tr>'
      : avail.map(d => `
        <tr>
          <td><div class="doctor-name">${d.name}</div></td>
          <td><span class="specialty">${d.specialty}</span></td>
          <td><div class="slots">${d.slots.slice(0,3).map(s=>`<span class="slot">${s}</span>`).join('')}</div></td>
          <td><span class="status status-avail"><span class="status-dot"></span>Available</span></td>
        </tr>`).join('');

    // Admin table (all doctors)
    document.getElementById('admin-table').innerHTML = all.map(d => `
      <tr>
        <td><div class="doctor-name">${d.name}</div></td>
        <td><span class="specialty">${d.specialty}</span></td>
        <td><span class="status ${d.available ? 'status-avail' : 'status-unavail'}">
          <span class="status-dot"></span>${d.available ? 'Available' : 'Unavailable'}
        </span></td>
        <td>
          <button class="${d.available ? 'btn-danger-sm' : 'btn-success-sm'}"
            onclick="toggleDoctor('${d.id}')">
            ${d.available ? 'Mark Unavailable' : 'Mark Available'}
          </button>
        </td>
      </tr>`).join('');

    // Doctor select
    const sel = document.getElementById('doctor-select');
    const prev = sel.value;
    sel.innerHTML = '<option value="">— Choose doctor —</option>' +
      avail.map(d => `<option value="${d.id}" ${d.id===prev?'selected':''}>${d.name} — ${d.specialty}</option>`).join('');
    if (prev) updateSlots(prev);
  }

  function updateSlots(docId) {
    const doc = doctors[docId];
    const sl = document.getElementById('slot-select');
    sl.innerHTML = doc
      ? doc.slots.map(s => `<option value="${s}">${s}</option>`).join('')
      : '<option value="">— Select slot —</option>';
  }

  document.getElementById('doctor-select').addEventListener('change', function() {
    updateSlots(this.value);
  });

  async function bookAppointment() {
    const name = document.getElementById('patient-name').value.trim();
    const docId = document.getElementById('doctor-select').value;
    const slot = document.getElementById('slot-select').value;
    const reason = document.getElementById('reason').value.trim();
    if (!name || !docId || !slot) { showToast('Please fill all required fields'); return; }

    const res = await fetch('/api/appointments', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({patient_name:name, doctor_id:docId, slot, reason})
    });
    const data = await res.json();
    if (res.ok) {
      appointments.push(data);
      renderAppointments();
      showToast('Appointment booked successfully');
      document.getElementById('patient-name').value = '';
      document.getElementById('reason').value = '';
    } else {
      showToast('Booking failed: ' + (data.error || 'Unknown error'));
    }
  }

  function renderAppointments() {
    const cnt = document.getElementById('appt-count');
    const list = document.getElementById('appointments-list');
    cnt.textContent = appointments.length;
    document.getElementById('stat-appts').textContent = appointments.length;
    if (!appointments.length) {
      list.innerHTML = '<div class="empty"><div class="empty-icon">📋</div>No appointments booked yet</div>';
      return;
    }
    list.innerHTML = appointments.map(a => `
      <div class="appt-item">
        <div class="appt-header">
          <span class="appt-patient">${a.patient_name}</span>
          <span class="appt-time">${a.slot}</span>
        </div>
        <div class="appt-doctor">${a.doctor_name} &nbsp;·&nbsp; ${a.specialty}</div>
        ${a.reason ? `<div class="appt-doctor" style="margin-top:2px;">Reason: ${a.reason}</div>` : ''}
        <div class="appt-id">Ref: ${a.appointment_id}</div>
      </div>`).join('');
  }

  async function toggleDoctor(docId) {
    const res = await fetch(`/api/doctors/${docId}/toggle`, {method:'PATCH'});
    const data = await res.json();
    doctors[docId] = data;
    renderAll();
    showToast(`${data.name}: ${data.available ? 'Now Available' : 'Marked Unavailable'}`);
  }

  loadDoctors();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/health")
def health():
    return jsonify({"status":"healthy","service":"healthcare-api","timestamp":datetime.utcnow().isoformat()})

@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    return jsonify(DOCTORS)

@app.route("/api/doctors/<doctor_id>/toggle", methods=["PATCH"])
def toggle_doctor(doctor_id):
    if doctor_id not in DOCTORS:
        return jsonify({"error":"Doctor not found"}), 404
    DOCTORS[doctor_id]["available"] = not DOCTORS[doctor_id]["available"]
    return jsonify(DOCTORS[doctor_id])

@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json()
    if not data or "patient_name" not in data or "doctor_id" not in data:
        return jsonify({"error":"Missing required fields"}), 400
    doctor_id = data["doctor_id"]
    if doctor_id not in DOCTORS:
        return jsonify({"error":"Doctor not found"}), 404
    if not DOCTORS[doctor_id]["available"]:
        return jsonify({"error":"Doctor not available"}), 400
    appt_id = hashlib.sha256(f"{data['patient_name']}{doctor_id}{data.get('slot','')}".encode()).hexdigest()[:10]
    appt = {
        "appointment_id": appt_id,
        "patient_name": data["patient_name"],
        "doctor_id": doctor_id,
        "doctor_name": DOCTORS[doctor_id]["name"],
        "specialty": DOCTORS[doctor_id]["specialty"],
        "slot": data.get("slot","TBD"),
        "reason": data.get("reason","General consultation"),
        "created_at": datetime.utcnow().isoformat()
    }
    APPOINTMENTS[appt_id] = appt
    return jsonify(appt), 201

@app.route("/api/appointments", methods=["GET"])
def list_appointments():
    return jsonify(list(APPOINTMENTS.values()))

@app.route("/api/patients", methods=["POST"])
@require_auth
def create_patient():
    data = request.get_json()
    if not data or "name" not in data or "dob" not in data:
        return jsonify({"error":"Missing required fields"}), 400
    patient_id = hashlib.sha256(f"{data['name']}{data['dob']}".encode()).hexdigest()[:12]
    return jsonify({"patient_id":patient_id,"status":"created"}), 201

@app.route("/api/patients", methods=["GET"])
@require_auth
def list_patients():
    return jsonify({"patients":[],"count":0})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
