from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="LinkedIn Post Generator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model (this creates JSON editor in Swagger)
class PostRequest(BaseModel):
    role: str
    tone: str
    purpose: str
    topic: str


# Health check route
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "LinkedIn Post Generator API is running"
    }


# Load custom writing style
def load_script_style():
    try:
        with open("scripts.txt", "r", encoding="utf-8") as file:
            return file.read()
    except:
        return "Write a professional LinkedIn post."


# Generate LinkedIn post
@app.post("/generatepost")
async def generate_post(data: PostRequest):

    role = data.role
    tone = data.tone
    purpose = data.purpose
    topic = data.topic

    script_style = load_script_style()

    prompt = f"""
Use this writing style:

{script_style}

Write a LinkedIn post.

Role: {role}
Tone: {tone}
Purpose: {purpose}
Topic: {topic}

Make the post engaging, authentic, and suitable for LinkedIn.
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional LinkedIn post writer."
            },
            {
                "role": "user",
                "content": prompt
            }
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

        if "choices" not in result:
            return {"error": result}

        generated_post = result["choices"][0]["message"]["content"]

        return {"post": generated_post}

    except Exception as e:
        return {"error": str(e)}