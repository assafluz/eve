from flask import Flask, request, jsonify, send_file
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv('.env')
print("Loaded .env file successfully")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ORGANIZATION_ID = os.getenv("OPENAI_ORGANIZATION_ID")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Print environment variables for debugging
print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
print(f"ORGANIZATION_ID: {ORGANIZATION_ID}")
print(f"ASSISTANT_ID: {ASSISTANT_ID}")

# Set up logging
logging.basicConfig(level=logging.ERROR)  # Configure logging level to capture errors

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
        'OpenAI-Organization': ORGANIZATION_ID
    }
    data = {
        'assistant_id': ASSISTANT_ID,
        'context': 'YOUR_CONVERSATION_CONTEXT'
    }

    try:
        # Create a new assistance session
        session_response = requests.post('https://api.openai.com/v1/assistants', json=data, headers=headers)
        session_response.raise_for_status()
        session_id = session_response.json()['id']

        # Send the user query to the assistant
        message = {
            'role': 'user',
            'content': user_query
        }
        response = requests.post(f'https://api.openai.com/v1/assistants/{session_id}/messages',
                                 json={'messages': [message]}, headers=headers)
        response.raise_for_status()

        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        logging.error(f"Error from OpenAI API: {error_message}")  # Log error message
        return jsonify({"error": "Failed to communicate with OpenAI API", "details": error_message}), 500


if __name__ == '__main__':
    app.run(debug=True)  # Consider setting debug to False in production
