from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware   # 👈 ADD THIS
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 👇 ADD CORS HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

RULES = """
- No parking in visitor area after 10 PM
- Pets must be on a leash in common areas
- No loud music after 11 PM
"""

class Query(BaseModel):
    question: str


@app.post("/ask")
def ask_question(query: Query):
    prompt = f"""
You are an assistant for a housing society.

Rules:
{RULES}

User Question:
{query.question}

Answer clearly based ONLY on the rules.
If not related, say contact society office.
"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "GrihaLink"
        },
        json={
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }
    )

    data = response.json()
    print("FULL RESPONSE:", data)

    if "choices" in data:
        answer = data["choices"][0]["message"]["content"]
    elif "error" in data:
        answer = data["error"]["message"]
    else:
        answer = "AI service temporarily unavailable"

    return {"answer": answer}