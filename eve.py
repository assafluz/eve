from flask import Flask, request, jsonify, send_file
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import re

# Load environment variables
load_dotenv('.env')
print("Loaded .env file successfully")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ORGANIZATION_ID = os.getenv("OPENAI_ORGANIZATION_ID")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Mask API key for printing and logging
masked_api_key = re.sub(r'(?<=.{16}).', '*', OPENAI_API_KEY)

# Set up logging
log_file = 'logs.txt'
logging.basicConfig(level=logging.INFO, filename=log_file,
                    filemode='w')  # Overwrite logs each time the application starts

# Log server initiation status
logging.info("Server initiated successfully.")


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
        'prompt': user_query,
        'model': 'gpt-4-turbo-preview',
        'max_tokens': 150,
        'temperature': 0.7
    }

    try:
        # Construct the correct URL for the OpenAI API request
        api_url = f'https://api.openai.com/v1/assistants/{ASSISTANT_ID}/messages'

        # Log request to OpenAI API
        logging.info(f"Sending request to OpenAI API with URL: {api_url} and data: {data}")

        response = requests.post(api_url, json=data, headers=headers)

        # Log response from OpenAI API
        logging.info(f"Received response from OpenAI API: {response.text}")

        response.raise_for_status()

        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        logging.error(f"Error from OpenAI API: {error_message}")  # Log error message
        print(f"Error from OpenAI API: {error_message}")  # Print error message to console
        return jsonify({"error": "Failed to communicate with OpenAI API", "details": error_message}), 500


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    print(f"Starting server at http://{host}:{port}")
    logging.info(f"Starting server at http://{host}:{port}")
    print(f"Organization ID: {ORGANIZATION_ID}")
    logging.info(f"Organization ID: {ORGANIZATION_ID}")
    print(f"Assistant ID: {ASSISTANT_ID}")
    logging.info(f"Assistant ID: {ASSISTANT_ID}")
    print(f"API Key: {masked_api_key}")
    logging.info(f"API Key: {masked_api_key}")
    app.run(debug=True, host=host, port=port)  # Consider setting debug to False in production
