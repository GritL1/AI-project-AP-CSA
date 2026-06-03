import os
import re
from fastapi import requests
from nicegui import ui
from openai import AsyncOpenAI, AuthenticationError
import json
import dotenv

import requests
dotenv.load_dotenv()
# 1. MAKE SURE THIS KEY STARTS WITH: sk-or-v1-
from dotenv import load_dotenv
load_dotenv()
MY_SECRET_KEY = os.getenv("MY_SECRET_KEY")  # Reads OpenRouter API key from
result = ""


# Initialize the Client directly using your hardcoded key string
client = AsyncOpenAI(
    base_url="https://openrouter.ai",
    api_key=MY_SECRET_KEY
)

def clean_html_error(html_text: str) -> str:
    """Helper to extract human-readable text out of an unexpected HTML response."""
    # Find the title or clear text blocks inside the HTML response
    title_match = re.search(r'<title>(.*?)</title>', html_text, re.IGNORECASE)
    desc_match = re.search(r'<meta name="description" content="(.*?)"', html_text, re.IGNORECASE)
    
    error_summary = "OpenRouter returned an HTML page instead of data.\n\n"
    if title_match:
        error_summary += f"Page Title: {title_match.group(1)}\n"
    if desc_match:
        error_summary += f"Description: {desc_match.group(1)}\n"
        
    error_summary += "\nPossible Fixes:\n1. Verify your key starts with 'sk-or-v1-'\n2. Ensure your OpenRouter account email is confirmed."
    return error_summary

async def fetch_probability(question: str, context: str):
    prompt = f"""
        Given the following context and question, provide a statistical probability based on searches through the internet (0% to 100%) 
        and a brief explanation based on the likelihood or truth of the statement.
        The question can be any question, but take in the context given in order to find data that show similar scenarios in order to return the statistical probability
        It doesn't matter if the question is satirical, or meant as a joke, or is a dumb question, always try and find sources to return a probability.

        Context: {context}
        Question: {question}

        Format exactly as: "Probability: [X]%\nReasoning: [Explanation]"
        """
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
    "Authorization": "Bearer " + MY_SECRET_KEY,
    "Content-Type": "application/json",
    },
    data=json.dumps({
    "model": "google/gemma-4-31b-it:free",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
        ],
    "reasoning": {"enabled": True}
    })
    )

    # Extract the assistant message with reasoning_details
    response = response.json()
    #print(response)  # Debug: Print the full response to understand its structure
    output = response['choices'][0]['message']['content']
    result = output

    # """Queries OpenRouter using a completely free open-source model."""
    # try:
    #     if MY_SECRET_KEY == "your-actual-openrouter-key-here" or not MY_SECRET_KEY:
    #         return "Error: You need to open main.py and replace placeholders with your real OpenRouter key string on line 6."

    #     prompt = f"""
    #     Given the following context and question, provide a statistical probability based on searches through the internet (0% to 100%) 
    #     and a brief explanation based on the likelihood or truth of the statement.
    #     The question can be any question, but take in the context given in order to find data that show similar scenarios in order to return the statistical probability
    #     It doesn't matter if the question is satirical, or meant as a joke, or is a dumb question, always try and find sources to return a probability.

    #     Context: {context}
    #     Question: {question}

    #     Format exactly as: "Probability: [X]%\nReasoning: [Explanation]"
    #     """
        
    #     response = await client.chat.completions.create(
    #         model="meta-llama/llama-3-8b-instruct:free",
    #         messages=[
    #             {"role": "system", "content": "You are a precise statistical analysis AI that can take in ANY question in order to return a statistical answer.."},
    #             {"role": "user", "content": prompt}
    #         ],
    #         extra_headers={
    #             "HTTP-Referer": "http://localhost:8080",
    #             "X-Title": "Statistical AI Project",
    #         }
    #     )
        

    #     # If OpenRouter gives a raw text block back instead of an object response
    #     if isinstance(response, str):
    #         if "<html" in response.lower():
    #             return clean_html_error(response)
    #         return f"OpenRouter Message:\n{response}"
            
    #     if hasattr(response, 'choices') and response.choices:
    #         return response.choices.message.content.strip()
            
    #     return f"Unexpected API response format: {str(response)}"
        
    # except AuthenticationError:
    #     return "Authentication Error: The API key pasted on line 6 is invalid. Double check that you copied the full key from openrouter.ai."
    # except Exception as e:
    #     # Check if the text of the exception contains HTML fragments
    #     err_str = str(e)
    #     if "<html" in err_str.lower():
    #         return clean_html_error(err_str)
    #     return f"Error analyzing data: {err_str}"

# Setup Dark Mode and Page Styling
ui.dark_mode().enable()
ui.query('body').style('background-color: #121212; color: white; font-family: Arial, sans-serif;')

# Global layout containers
with ui.column().classes('w-full max-w-2xl mx-auto p-8 mt-12'):
    ui.label('Statistical AI Analyzer').classes('text-5xl font-bold mb-2 text-blue-500')
    ui.label('Type in any question and provide context for said question, and a statistical probability for said question will occur. The type of question does not matter(Ex. An unserious/joke question will return a probability all the same.)').classes('text-sm text-yellow-400 mb-6 tracking-wider')

    question_input = ui.input(label='Your Question').classes('w-full mb-4')
    context_input = ui.textarea(label='Context / Background Data').classes('w-full mb-6').props('rows=4')
    
    with ui.card().classes('w-full p-6 bg-gray-800 text-white mt-4') as result_card:
        result_text = ui.label(result).classes('text-lg font-medium whitespace-pre-line')
    
    result_card.set_visibility(False)

    spinner = ui.spinner('dots', size='lg').classes('mx-auto mt-4')
    spinner.set_visibility(False)

    async def on_submit():
        if not question_input.value or not context_input.value:
            ui.notify('Please provide both a question and context!', color='negative')
            return

        submit_btn.disable()
        spinner.set_visibility(True)
        result_card.set_visibility(False)
        ui.notify('Analyzing trends via OpenRouter...', color='info')

        try:
            response = await fetch_probability(question_input.value, context_input.value)
            result_text.set_text(response)
            result_card.set_visibility(True)
        except Exception as ex:
            ui.notify(f'An error occurred: {ex}', color='negative')
        finally:
            submit_btn.enable()
            spinner.set_visibility(False)

    submit_btn = ui.button('Calculate Probability', on_click=on_submit).classes('w-full bg-blue-600 text-white py-3 mt-4').style('border-radius: 8px;')

# Run the app
ui.run(title="Statistical AI", port=8080, host='0.0.0.0')
