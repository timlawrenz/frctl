#!/usr/bin/env python3
"""Simple test with direct Google Generative AI SDK."""

import os
import sys
import google.generativeai as genai

# Load .env
from pathlib import Path
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not set")
    sys.exit(1)

genai.configure(api_key=api_key)

# Test simple generation
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = """Is this goal atomic (simple enough to implement directly) or composite (needs to be broken into sub-goals)?

Goal: Create a simple todo list web application

Respond with ONLY this JSON structure:
{
    "is_atomic": false,
    "reasoning": "explanation here"
}"""

print("Testing Gemini API...")
print("Prompt:", prompt[:100], "...")

response = model.generate_content(prompt)
print("\nResponse:")
print(response.text)
print("\n✅ Gemini API works!")
