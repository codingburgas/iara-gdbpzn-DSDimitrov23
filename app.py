from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

vessels = [
    {
        "id": 1, 
        "cfr": "BGR001", 
        "name": "Black Sea Hunter", 
        "captain": "Ivan Ivanov",
        "tonnage": 15.5, 
        "length": 12.0,
        "engine_power": 120
    }
]

permits = [
    {
        "vessel_id": 1, 
        "valid_until": "2026-12-31", 
        "gears": ["Net", "Fishing Rod"], 
        "active": True
    }
]

@app.route("/")
def home():
    return "IARA Information System"

@app.route("/vessels")
def get_vessels():
    return jsonify(vessels)

@app.route("/check_permit/<string:cfr>")
def check_permit(cfr):
    vessel = next((v for v in vessels if v["cfr"] == cfr), None)
    if not vessel:
        return jsonify({"error": "Vessel not found"}), 404
    
    permit = next((p for p in permits if p["vessel_id"] == vessel["id"]), None)
    if permit and permit["active"]:
        return jsonify({
            "status": "Valid", 
            "vessel": vessel["name"], 
            "expires": permit["valid_until"]
        })
    return jsonify({"status": "Invalid or missing permit"}), 403

if __name__ == "__main__":
    app.run(debug=True)