# src/persona_builder.py

import os
import openai
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Set up Groq API access
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"
model_name = os.getenv("GROQ_MODEL", "llama3-70b-8192")  # Recommended current model

def clean_json(json_str):
    # Remove comments (// ...) which are not valid in JSON
    return re.sub(r'//.*', '', json_str)

def extract_persona(posts_and_comments_text, username):
    prompt = f"""
You are an AI persona extractor. Based on the Reddit posts and comments below, generate a structured **JSON** persona with the following format:

{{
  "location": "Location or blank",
  "archetype": "1-line title",
  "quote": "Short representative quote",
  "motivations": {{
    "Motivation 1": value (0–100),
    "Motivation 2": value (0–100)
  }},
  "personality": {{
    "Trait 1": value (0–100),
    "Trait 2": value (0–100)
  }},
  "behaviors": ["...", "..."],
  "goals": ["...", "..."],
  "frustrations": ["...", "..."]
}}

Do NOT include explanations or markdown. Just return the JSON.

--- USER POSTS AND COMMENTS ---

{posts_and_comments_text}
"""

    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful JSON-generating assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        raw = response["choices"][0]["message"]["content"]
        cleaned = clean_json(raw)

        persona_dict = json.loads(cleaned)

        os.makedirs("data", exist_ok=True)
        json_path = f"data/{username}_persona.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(persona_dict, f, indent=2)

        return persona_dict

    except Exception as e:
        raise RuntimeError(f"[ERROR] Groq failed: {e}")
