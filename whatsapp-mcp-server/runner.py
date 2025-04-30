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



from flask import Flask, Response
import time
import json
from flask import jsonify
from mcp.server.fastmcp import FastMCP
from flask import Flask, render_template
from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media
)
app = Flask(__name__)
@app.route('/tools', methods=['GET'])
def list_tools():
    """Endpoint to list all tools and their descriptions."""
    tools = {
        "search_contacts": whatsapp_search_contacts,
        "list_messages": whatsapp_list_messages,
        "list_chats": whatsapp_list_chats,
        "get_chat": whatsapp_get_chat,
        "get_direct_chat_by_contact": whatsapp_get_direct_chat_by_contact,
        "get_contact_chats": whatsapp_get_contact_chats,
        "get_last_interaction": whatsapp_get_last_interaction,
        "get_message_context": whatsapp_get_message_context,
        "send_message": whatsapp_send_message,
        "send_file": whatsapp_send_file,
        "send_audio_message": whatsapp_audio_voice_message,
        "download_media": whatsapp_download_media
    }

    # Prepare the tools data for rendering
    tools_info = [
        {"name": tool_name, "description": tool.__doc__}
        for tool_name, tool in tools.items()
    ]
    
    # Render the HTML template with tools data
    return render_template('tools.html', tools_info=tools_info)




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
