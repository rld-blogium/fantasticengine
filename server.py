# server.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import json, os

server_bp = Blueprint('server_bp', __name__)

LICENSE_FILE = "licenses.json"
signals = {}

def load_licenses():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=2)

licenses = load_licenses()

def is_valid_license(license_id):
    expiry_str = licenses.get(license_id)
    if not expiry_str:
        return False
    try:
        expiry = datetime.fromisoformat(expiry_str)
        return datetime.now(timezone.utc) < expiry
    except ValueError:
        return False

@server_bp.route("/signal/<license_id>", methods=["POST"])
def receive_signal(license_id):
    if not is_valid_license(license_id):
        return jsonify({"error": "License expired or invalid"}), 403
    data = request.get_json()
    if not data:
        return "Missing JSON", 400
    signals[license_id] = data
    print(f"✅ Signal for {license_id}: {data}")
    return "Signal queued", 200

@server_bp.route("/get_signal/<license_id>", methods=["GET"])
def get_signal(license_id):
    if not is_valid_license(license_id):
        return jsonify({"error": "License expired or invalid"}), 403
    return jsonify(signals.get(license_id, {}))

@server_bp.route("/ack_signal/<license_id>", methods=["POST"])
def ack_signal(license_id):
    if license_id in signals:
        print(f"✅ Acknowledged signal for {license_id}")
        signals.pop(license_id, None)
    return "Acknowledged", 200

@server_bp.route("/licenses", methods=["GET", "POST", "DELETE", "PUT"])
def manage_licenses():
    global licenses
    if request.method == "GET":
        return jsonify(licenses)
    elif request.method == "POST":
        data = request.get_json()
        licenses[data["license_id"]] = data["expiry"]
        save_licenses(licenses)
        return "License added", 201
    elif request.method == "DELETE":
        data = request.get_json()
        licenses.pop(data["license_id"], None)
        save_licenses(licenses)
        return "License deleted", 200
    elif request.method == "PUT":
        data = request.get_json()
        licenses[data["license_id"]] = data["expiry"]
        save_licenses(licenses)
        return "License updated", 200
