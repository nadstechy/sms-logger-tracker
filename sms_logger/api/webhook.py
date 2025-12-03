from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# Initialize Firebase
if not firebase_admin._apps:
    private_key = os.environ.get('FIREBASE_PRIVATE_KEY')
    if private_key:
        private_key = private_key.replace('\\n', '\n')

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
        "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()

# IMPORTANT: This route must match the file path '/api/webhook'
@app.route('/api/webhook', methods=['POST'])
def webhook_handler():
    # 1. Security Check
    secret = request.headers.get('x-api-secret')
    if secret != os.environ.get('API_SECRET'):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        sender = data.get('sender', 'Unknown')
        message = data.get('message', '')
        
        doc_ref = db.collection('messages').add({
            'sender': sender,
            'message': message,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

        return jsonify({"success": True, "id": doc_ref[1].id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This is required for Vercel to find the app
if __name__ == '__main__':
    app.run()
