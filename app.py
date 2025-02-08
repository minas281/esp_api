from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Διαδρομή βάσης δεδομένων
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'test.db')}"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Δημιουργία του πίνακα Measurement
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    battery = db.Column(db.Float, nullable=False)
    rssi = db.Column(db.Integer, nullable=False)

# ✅ Δημιουργία της βάσης και των πινάκων
with app.app_context():
    db.create_all()
    print("✅ Database and tables created successfully!")

# ✅ Route για αποστολή δεδομένων
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    if not data or 'device' not in data or 'temperature' not in data or 'battery' not in data or 'rssi' not in data:
        return jsonify({"error": "Invalid data"}), 400

    measurement = Measurement(
        device=data['device'],
        temperature=data['temperature'],
        battery=data['battery'],
        rssi=data['rssi']
    )

    db.session.add(measurement)
    db.session.commit()

    return jsonify({"message": "Data received"}), 201

# ✅ Route για λήψη όλων των δεδομένων
@app.route('/data', methods=['GET'])
def get_data():
    measurements = Measurement.query.all()
    results = [
        {
            "id": m.id,
            "device": m.device,
            "temperature": m.temperature,
            "battery": m.battery,
            "rssi": m.rssi
        }
        for m in measurements
    ]
    return jsonify(results)

# ✅ Route για διαγραφή όλων των δεδομένων
@app.route('/data', methods=['DELETE'])
def delete_data():
    try:
        num_deleted = db.session.query(Measurement).delete()
        db.session.commit()
        return jsonify({"message": f"Deleted {num_deleted} records"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
