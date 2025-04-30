import google.generativeai as genai
import subprocess
from fastapi import FastAPI, Request
import importlib.util
import os
from pathlib import Path

def load_send_message(path_to_main_py):
    # Construct a module spec
    spec = importlib.util.spec_from_file_location(
        "whatsapp_main", Path(path_to_main_py).resolve()
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.send_message


from flask import Flask, Response
import time
import json
from flask import jsonify
from mcp.server.fastmcp import FastMCP
from flask import Flask, render_template
app = Flask(__name__)

# Configure Gemini
genai.configure(api_key="AIzaSyD8bwyn4220ZKL9biFi3_46tRlgKrZETbg")


send_message = load_send_message(os.path.join(os.getcwd(), "main.py"))

# def send_whatsapp_message(recipient: str, message: str):
#     """Directly execute MCP tool using subprocess"""
#     try:
#         print("sending.....")
#         # subprocess.run([
#         #     "python", 
#         #     "/Users/bhumikamakwana/Desktop/clost_web/whatsapp-mcp/whatsapp-mcp-server/main.py",
#         #     "send_message",
#         #     "--recipient",
#         #     recipient,
#         #     "--message",
#         #     message
#         # ], check=True)
#         pass
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to send message: {str(e)}")
#         raise

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

# @app.post("/incoming")
# async def handle_message(request: Request):
#     data = await request.json()
#     message = data.get("text")
#     sender = data.get("from")

#     if not message or not sender:
#         return {"error": "Missing message or sender"}

#     try:
#         # Generate response with Gemini
#         gemini_response = generate_gemini_response(message)
#         print(gemini_response)
        
#         # Send response directly using MCP tool
#         #send_whatsapp_message(recipient=sender, message=gemini_response)
#         res = send_message(sender, gemini_response)
        
#         return {"status": "Message processed successfully"}
        
#     except Exception as e:
#         return {"error": str(e)}
    
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