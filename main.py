from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore
import threading

# Initialize FastAPI app
app = FastAPI()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")  # Update with correct path
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Global variable to store the latest document
latest_data = {}

# Function to fetch the latest document with all fields
def get_latest_sensor_data():
    doc_ref = db.collection("sensor_data").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    docs = doc_ref.stream()
    
    for doc in docs:
        return doc.to_dict()  # Return the entire document
    
    return {"message": "No data available"}

# Firestore real-time listener function
def on_snapshot(doc_snapshot, changes, read_time):
    global latest_data

    if doc_snapshot:
        # Get the latest document
        latest_doc = doc_snapshot[-1]  
        latest_data = latest_doc.to_dict()  # Store the full document

        # Print new data
        print("\n🔥 New Sensor Data Received:")
        for key, value in latest_data.items():
            print(f"{key}: {value}")
        print("---------------------------------------------------")

# Start real-time listener
def listen_to_firestore():
    doc_ref = db.collection("sensor_data_test").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    doc_ref.on_snapshot(on_snapshot)

# Start listening in a separate thread
threading.Thread(target=listen_to_firestore, daemon=True).start()

# API route to get the latest sensor data
@app.get("/latest-data")
def latest_data_endpoint():
    return latest_data or {"message": "No data available"}