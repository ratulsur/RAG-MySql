# app/rag/groq_client.py
import os
from groq import Groq

class GroqLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, prompt: str) -> str:
        """
        Simple wrapper for text generation.
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.0
        )
        return response.choices[0].message["content"]
