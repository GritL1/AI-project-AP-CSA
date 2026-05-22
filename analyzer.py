# analyzer.py
# This module handles all AI-powered document analysis using DeepSeek API.

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the DeepSeek client (OpenAI-compatible)
# DeepSeek API base URL is different from OpenAI's.
client = OpenAI( #Variable client that does the talking
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # Reads API key from environment
    base_url="https://api.deepseek.com"      # DeepSeek access
)

def analyze_document(text: str):
        # System prompt: defines AI's role and output format
    system_prompt = """
    You are an expert document analyst. Analyze the provided document and return a structured analysis in the following JSON format:
    {
        "summary": "A concise 2-3 sentence summary of the document.",
        "sentiment": "Positive / Neutral / Negative (with brief reasoning)",
        "key_topics": ["topic1", "topic2", "topic3"],
        "action_items": ["action1", "action2"] or "No clear action items found."
    }
    Keep each field concise and useful.
    """
    # User prompt: contains the actual document text
    user_prompt = f"Document to analyze:\n\n{text}"

    try:
    # Call DeepSeek API
        response = client.chat.completions.create(
        model="deepseek-chat",  # DeepSeek's free chat model
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower = more deterministic, factual output
            max_tokens=800    # Enough for structured analysis
        )
                # Extract the AI's reply
        ai_response = response.choices[0].message.content
        {
  "choices": [
    {
      "message": {
        "content": "The AI's actual response text goes here"
      }
    }
  ]
}
                # Basic validation: ensure it contains JSON-like structure
        if not ("summary" in ai_response and "sentiment" in ai_response):
            raise ValueError("AI response missing expected fields")
                return ai_response
            except Exception as e:
        # Return a graceful error message as a pseudo-JSON string
        return f'{{"summary": "Analysis failed.", "sentiment": "Error", "key_topics": [], "action_items": ["Error: {str(e)}"]}}'