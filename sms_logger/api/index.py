from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = Flask(__name__)

# Initialize Firebase only if it hasn't been initialized yet
if not firebase_admin._apps:
    # Handle the private key newline issue for Vercel Environment Variables
    private_key = os.environ.get('FIREBASE_PRIVATE_KEY')
    if private_key:
        private_key = private_key.replace('\\n', '\n')

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
        "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'), # Optional, but good practice
        "private_key": private_key,
        "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/api/index', methods=['POST'])
def webhook():
    # 1. Security Check
    secret = request.headers.get('x-api-secret')
    if secret != os.environ.get('API_SECRET'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # 2. Get Data from Request
        data = request.json
        sender = data.get('sender', 'Unknown')
        message_body = data.get('message', '')
        timestamp = data.get('timestamp', firestore.SERVER_TIMESTAMP)

        # 3. Store in Firestore "messages" collection
        doc_ref = db.collection('messages').add({
            'sender': sender,
            'message': message_body,
            'timestamp': timestamp,
            'created_at': firestore.SERVER_TIMESTAMP
        })

        return jsonify({"success": True, "id": doc_ref[1].id}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# For Vercel to handle the request
if __name__ == '__main__':
    app.run()