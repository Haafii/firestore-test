# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from threading import Thread

# app = FastAPI()

# cred = credentials.Certificate("serviceAccountKey.json")  # Replace with your service account key file path
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# latest_data = {}

# def get_latest_sensor_data():
#     doc_ref = db.collection("sensor_data").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
#     docs = doc_ref.stream()
    
#     for doc in docs:
#         return doc.to_dict()  # Return the entire document
    
#     return {"message": "No data available"}
# def on_snapshot(doc_snapshot, changes, read_time):
#     global latest_data

#     if doc_snapshot:
#         # Get the latest document
#         latest_doc = doc_snapshot[-1]  
#         latest_data = latest_doc.to_dict()  # Store the full document

#         # Print new data
#         print("\n🔥 New Sensor Data Received:")
#         for key, value in latest_data.items():
#             print(f"{key}: {value}")
#         print("---------------------------------------------------")

# # Start real-time listener
# def listen_to_firestore():
#     doc_ref = db.collection("sensor_data_test").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
#     doc_ref.on_snapshot(on_snapshot)

# # Start listening in a separate thread
# Thread(target=listen_to_firestore, daemon=True).start()

# # API route to get the latest sensor data
# @app.get("/latest-data")
# def latest_data_endpoint():
#     return latest_data or {"message": "No data available"}




import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from threading import Thread, Lock
import time
import os
import json

# Initialize FastAPI app
app = FastAPI()

# Initialize Firebase Admin SDK
# Get the service account JSON from the environment variable
service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
if service_account_json:
    cred_dict = json.loads(service_account_json)  # Parse the JSON string
    cred = credentials.Certificate(cred_dict)  # Create credentials object
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("Firebase service account key is missing")
db = firestore.client()

# Global data and lock for thread safety
latest_data = {}
data_lock = Lock()

# Function to fetch the latest sensor data from Firestore
def get_latest_sensor_data():
    doc_ref = db.collection("sensor_data_test").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    docs = doc_ref.stream()
    
    for doc in docs:
        return doc.to_dict()  # Return the entire document
    
    return {"message": "No data available"}

# Callback function for Firestore real-time listener
def on_snapshot(doc_snapshot, changes, read_time):
    global latest_data

    if doc_snapshot:
        # Get the latest document
        latest_doc = doc_snapshot[-1]  
        
        # Update the global latest_data safely using lock
        with data_lock:
            latest_data = latest_doc.to_dict()  # Store the full document

        # Print new data to console
        print("\n🔥 New Sensor Data Received:")
        for key, value in latest_data.items():
            print(f"{key}: {value}")
        print("---------------------------------------------------")

# Function to start listening to Firestore in a separate thread
def listen_to_firestore():
    doc_ref = db.collection("sensor_data_test").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    doc_ref.on_snapshot(on_snapshot)

# Start the Firestore listener in a separate thread
Thread(target=listen_to_firestore, daemon=True).start()

# API route to get the latest sensor data
@app.get("/latest-data")
def latest_data_endpoint():
    # Return the latest data using lock for thread safety
    with data_lock:
        if latest_data:
            return latest_data
        else:
            return {"message": "No data available"}