import firebase_admin
from firebase_admin import credentials, firestore
import random
import time
from datetime import datetime

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")  # Replace with your service account key file path
firebase_admin.initialize_app(cred)

db = firestore.client()

def generate_random_data():
    """Generates random sensor data with all required fields."""
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    speed = random.uniform(0, 100)  # Adjust as needed

    # Generate ride_id using timestamp (YYYYMMDDHHMMSS format)
    ride_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    return {
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,
        "ride_id": ride_id,
        "timestamp": firestore.SERVER_TIMESTAMP  # Firestore will set the exact time
    }

def upload_data_periodically(interval_seconds=5):
    """Uploads data to Firestore at a specified interval."""
    try:
        while True:
            data = generate_random_data()
            doc_ref = db.collection("sensor_data_test").document()
            doc_ref.set(data)
            print(f"✅ Data added! Document ID: {doc_ref.id}\n{data}")
            time.sleep(interval_seconds)  # Wait for the specified interval

    except KeyboardInterrupt:
        print("🛑 Data upload stopped by user.")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    upload_data_periodically(2)  # Upload data every 2 seconds
