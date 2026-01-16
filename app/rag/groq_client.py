# app/rag/groq_client.py
from __future__ import annotations

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GroqLLM:
    def __init__(self, model_name: str):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        self.model_name = model_name
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        # ✅ IMPORTANT: use attribute access
        return resp.choices[0].message.content.strip()
