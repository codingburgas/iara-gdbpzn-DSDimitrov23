from flask import Flask, jsonify

app = Flask(__name__)

boats = [
    {"id": 1, "name": "Black Sea Hunter", "captain": "Ivan Ivanov"},
    {"id": 2, "name": "Sea Star", "captain": "Petar Petrov"}
]

@app.route("/")
def home():
    return "IARA Fishing System"

@app.route("/boats")
def get_boats():
    return jsonify(boats)

if __name__ == "__main__":
    app.run(debug=True)