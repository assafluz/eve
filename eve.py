from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

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
masked_api_key = "*" * (len(OPENAI_API_KEY) - 4) + OPENAI_API_KEY[-4:]

# Set up logging
log_file = 'logs.txt'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file,
                    filemode='w')

# Log server initiation status and current time only once
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.info(f"{current_time}: Server initiated successfully.")
print(f"{current_time}: Server initiated successfully.")


def create_thread():
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
        'OpenAI-Organization': ORGANIZATION_ID,
        'OpenAI-Beta': 'assistants=v1'
    }
    data = {}

    try:
        api_url = f'https://api.openai.com/v1/threads'
        response = requests.post(api_url, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get('id')
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        logging.error(f"Error from OpenAI API: {error_message}")
        return None


def add_message_to_thread(thread_id, content):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
        'OpenAI-Organization': ORGANIZATION_ID,
        'OpenAI-Beta': 'assistants=v1'
    }
    data = {
        'role': 'user',
        'content': content
    }

    try:
        api_url = f'https://api.openai.com/v1/assistants/{ASSISTANT_ID}/'
        response = requests.post(api_url, json=data, headers=headers)

        # Log request and response details to logs.txt
        logging.info(f"Request to OpenAI API: POST {api_url}, Headers: {headers}, Body: {data}")
        logging.info(f"Response from OpenAI API: Status Code - {response.status_code}, Body - {response.text}")

        # Print request and response details to console
        print(f"Request to OpenAI API: POST {api_url}, Headers: {headers}, Body: {data}")
        print(f"Response from OpenAI API: Status Code - {response.status_code}, Body - {response.text}")

        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        logging.error(f"Error from OpenAI API: {error_message}")
        return False


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    thread_id = create_thread()
    if not thread_id:
        return jsonify({"error": "Failed to create conversation thread"}), 500

    if not add_message_to_thread(thread_id, user_query):
        return jsonify({"error": "Failed to add message to conversation thread"}), 500

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
        'OpenAI-Organization': ORGANIZATION_ID,
        'OpenAI-Beta': 'assistants=v1'
    }
    data = {
        'prompt': user_query,
        'model': 'gpt-4-turbo-preview',
        'max_tokens': 150,
        'temperature': 0.7
    }

    try:
        api_url = f'https://api.openai.com/v1/assistants/{ASSISTANT_ID}/'
        print(f"API URL: {api_url}")
        print(f"Request to OpenAI API: POST {api_url}")
        print(f"Request body: {data}")
        print(f"Request headers: {headers}")

        response = requests.post(api_url, json=data, headers=headers)

        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")

        logging.info(f"Request to OpenAI API: POST {api_url}, Headers: {headers}, Body: {data}")
        logging.info(f"Response from OpenAI API: Status Code - {response.status_code}, Body - {response.text}")

        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        logging.error(f"Error from OpenAI API: {error_message}")
        return jsonify({"error": "Failed to fetch response from OpenAI API"}), 500


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
    app.run(debug=True, host=host, port=port)
