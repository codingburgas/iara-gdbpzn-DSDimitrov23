from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Mock Data (Database)
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

# Route to serve the HTML page
@app.route("/")
def home():
    return render_template("index.html")

# API Endpoint for permit checking
@app.route("/api/check_permit/<string:cfr>")
def check_permit(cfr):
    vessel = next((v for v in vessels if v["cfr"].upper() == cfr.upper()), None)
    
    if not vessel:
        return jsonify({"error": "Vessel not found"}), 404
    
    permit = next((p for p in permits if p["vessel_id"] == vessel["id"]), None)
    
    if permit and permit["active"]:
        return jsonify({
            "status": "Valid", 
            "vessel": vessel["name"], 
            "expires": permit["valid_until"]
        })
    
    return jsonify({"status": "Invalid or expired permit"}), 403

if __name__ == "__main__":
    app.run(debug=True)