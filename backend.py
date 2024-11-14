import requests
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configuration for OpenAI
API_KEY = "7f6d5cc4da8f455f85c47d6c60dc6fac"  # Replace with your actual API key
ENDPOINT = "https://genai-openai-lighteninglancers.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Function to send a message to the OpenAI API
def get_ai_response(user_input):
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "user", "content": user_input},
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
    }

    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the response code is not 200
        response_data = response.json()
        ai_message = response_data['choices'][0]['message']['content']
        return ai_message
    except requests.RequestException as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't get a response from the AI."

# API endpoint for getting AI response
@app.route("/get-ai-response", methods=["POST"])
def chat():
    # Check if the request has JSON content and a 'message' key
    if not request.is_json:
        return jsonify({"error": "Invalid request format. Expected JSON."}), 400

    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Get AI's response
    ai_response = get_ai_response(user_input)
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    app.run(debug=True)
