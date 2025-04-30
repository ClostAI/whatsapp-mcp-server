import google.generativeai as genai
import subprocess
from fastapi import FastAPI, Request
import importlib.util
import os
from pathlib import Path
from flask import Flask, Response
import time
import json
from flask import jsonify
from mcp.server.fastmcp import FastMCP
from flask import Flask, render_template


def load_send_message(path_to_main_py):
    # Construct a module spec
    spec = importlib.util.spec_from_file_location(
        "whatsapp_main", Path(path_to_main_py).resolve()
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.send_message

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key= os.getenv("GENAI_API_KEY"))


send_message = load_send_message(os.path.join(os.getcwd(), "main.py"))

def generate_gemini_response(prompt: str) -> str:
    """Generate response using Gemini 1.5 Flash model"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "text/plain"
        }
    )
    return response.text

from flask import Flask, request, jsonify
@app.post("/incoming")
def handle_message():
    data = request.get_json()
    message = data.get("text")
    sender  = data.get("from")

    if not message or not sender:
        return jsonify(error="Missing message or sender"), 400

    try:
        gemini_response = generate_gemini_response(message)
        send_message(sender, gemini_response)
        return jsonify(status="Message processed successfully")
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    # Run the Flask app to handle SSE
    app.run(debug=True, threaded=True, host="0.0.0.0", port=8000)
