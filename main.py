from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/")
def home():
    return {"status": "ok", "message": "LinkedIn Post Generator API"}

# Load custom script style
def load_script_style():
    try:
        with open("scripts.txt", "r", encoding="utf-8") as file:
            return file.read()
    except:
        return "Write a professional LinkedIn post."

# Generate LinkedIn post
@app.post("/generatepost")
async def generate_post(request: Request):

    data = await request.json()

    role = data.get("role", "Student")
    tone = data.get("tone", "Professional")
    purpose = data.get("purpose", "Career update")
    topic = data.get("topic", "General")

    script_style = load_script_style()

    prompt = f"""
Use this writing style:

{script_style}

Write a LinkedIn post.

Role: {role}
Tone: {tone}
Purpose: {purpose}
Topic: {topic}

Match the tone and format.
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional LinkedIn post writer."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
    }

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()

        generated_post = result["choices"][0]["message"]["content"]

        return {"post": generated_post}

    except Exception as e:
        return {"error": str(e)}