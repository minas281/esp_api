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

# ✅ Νέος πίνακας για αποθήκευση ολόκληρου του μηνύματος
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)  # Ολόκληρο το μήνυμα αποθηκεύεται εδώ
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())  # Χρόνος καταγραφής

# ✅ Δημιουργία της βάσης και των πινάκων
with app.app_context():
    db.create_all()
    print("✅ Database and tables created successfully!")

# ✅ Route για αποστολή δεδομένων
@app.route('/data', methods=['POST'])
def receive_data():
    try:
        raw_data = request.data.decode("utf-8")  # Διαβάζουμε τα ακατέργαστα δεδομένα
        print(f"🔍 RAW Received Data: {raw_data}")

        data = request.get_json(silent=True)

        if not data:
            print("❌ JSON Parsing Error! Possible encoding issue.")
            return jsonify({"error": "Invalid JSON format"}), 400

        print("🔍 Parsed JSON Data:", data)

        if 'message' not in data:
            print("❌ Missing 'message' field!")
            return jsonify({"error": "Invalid data, 'message' is required"}), 400

        measurement = Measurement(
            message=data['message']
        )

        db.session.add(measurement)
        db.session.commit()

        print(f"✅ Data saved successfully! Message: {data['message']}")
        return jsonify({"message": "Data received"}), 201

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Route για λήψη όλων των δεδομένων
@app.route('/data', methods=['GET'])
def get_data():
    measurements = Measurement.query.order_by(Measurement.id.desc()).all()  # Φέρνει τα πιο πρόσφατα πρώτα
    results = [
        {
            "id": m.id,
            "message": m.message,  # Επιστρέφουμε το ολόκληρο το μήνυμα
            "timestamp": m.timestamp
        }
        for m in measurements
    ]
    print("🔍 Sending data:", results)  # Debugging
    return jsonify(results)

# ✅ Route για διαγραφή όλων των δεδομένων
@app.route('/data', methods=['DELETE'])
def delete_data():
    try:
        num_deleted = db.session.query(Measurement).delete()
        db.session.commit()
        print(f"✅ Deleted {num_deleted} records from database.")
        return jsonify({"message": f"Deleted {num_deleted} records"}), 200
    except Exception as e:
        db.session.rollback()
        print("❌ Error deleting records:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
