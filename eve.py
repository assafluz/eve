from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('.eve')
print("Loaded .env file successfully")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Print environment variables for debugging
print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
print(f"ASSISTANT_ID: {ASSISTANT_ID}")


@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "messages": [{"role": "user", "content": user_query}]
    }
    try:
        response = requests.post(f'https://api.openai.com/v1/assistants/{ASSISTANT_ID}/messages', json=data, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the response is not 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response.json())


if __name__ == '__main__':
    app.run(debug=True)  # Consider setting debug to False in production
