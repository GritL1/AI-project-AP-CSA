import os
import re
from fastapi import requests
from nicegui import app, ui
from openai import AsyncOpenAI, AuthenticationError
import json
import dotenv
import time


import requests
dotenv.load_dotenv()
from dotenv import load_dotenv
load_dotenv()
MY_SECRET_KEY = os.getenv("MY_SECRET_KEY")  




app.add_static_files('/static-fonts', '/workspaces/AI-project-AP-CSA/assets/fonts/')




# 2. Add the custom font to the page's CSS using @font-face
ui.add_head_html('''
    <style>
        @font-face {
            font-family: 'Mythshire';
            src: url('/static-fonts/Mythshire Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
   
    @keyframes rainbow-text {
        0% { color: #ff0000; }
        20% { color: #ff9900; }
        40% { color: #ffff00; }
        60% { color: #00cc00; }
        80% { color: #0099ff; }
        95% { color: #9900ff; }
        100% { color: #ff0000; }
    }




    .animated-rainbow {
        animation: rainbow-text 8s infinite;
        font-size: 8xl;
        font-weight: bold;
    }
                 
    .animated-rainbow-small {
        animation: rainbow-text 8s infinite;
        font-size: lg;
        font-weight: bold;
    }
    </style>
''')




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




# ADDITION: Explicit tracking variable to safely limit local recursion retries if the entire free platform is down
async def fetch_probability(question: str, context: str, attempt=0):
    # ADDITION: Cap loop attempts at 3 to prevent infinite visual spinning if OpenRouter encounters global downtime
    if attempt >= 3:
        raise Exception("OpenRouter's collective free model pool is fully congested or rate-limited right now. Please try again in a few minutes.")




    # ADDITION: Inform console logging that the app is utilizing OpenRouter's internal zero-cost load balance wrapper
    print(f"Routing request dynamically via OpenRouter's universal fallback wrapper (Attempt {attempt + 1})")




    prompt = f"""
        Given the following context and question, provide a statistical probability based on searches through the internet (0% to 100%)
        and a brief explanation based on the likelihood or truth of the statement. The probability MUST be an integer. 
        The question can be any question, but take in the context given in order to find data that show similar scenarios in order to return the statistical probability
        It doesn't matter if the question is satirical, or meant as a joke, or is a dumb question, always try and find sources to return a probability.
        You are able to comprehend and understand internet slang terms. If there is a word within the prompt that feels out of place or doesn't follow standard english conventions, search it up as it is most likely internet slang




        Context: {context}
        Question: {question}




        Format exactly as: "Probability: [X]%\nReasoning: [Explanation]"
        """
       
    # ADDITION: Construct the base payload to query the automatic router endpoint
    payload_data = {
        # MODIFICATION: Replaced the fixed Gemma string ID with the unified free models router identifier
        "model": "openrouter/free",
        "messages": [
            { "role": "system", "content": "You are a precise statistical analysis AI that can take in ANY question in order to return a statistical answer."},
            {"role": "user", "content": prompt}
        ]
    }
   
    # ADDITION: Conditionally apply reasoning paths only on initial tries.
    # Because 'openrouter/free' can route to smaller non-reasoning models,
    # strip this parameter if a retry occurs to avoid unsupported parameter syntax errors on the fallback models.
    if attempt == 0:
        payload_data["reasoning"] = {
            "max_tokens": 1500,
            "enabled": True
        }




    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + MY_SECRET_KEY,
            "Content-Type": "application/json",
        },
        data=json.dumps(payload_data)
    )




    # ADDITION: Process a server-side 429 rate limit or gateway timeout gracefully by retrying
    if response.status_code in [429, 502, 503, 504]:
        print(f"The global pool returned status {response.status_code}. Waiting 5 seconds before asking OpenRouter to shift to a different available model...")
        time.sleep(5)
        return await fetch_probability(question, context, attempt=attempt + 1)




    # ADDITION: Route unexpected HTML pages through your error formatting utility
    if "text/html" in response.headers.get("Content-Type", ""):
        print("Received HTML string content. Retrying connection payload...")
        time.sleep(2)
        return await fetch_probability(question, context, attempt=attempt + 1)




    # Extract the assistant message with reasoning_details
    response = response.json()
    print(response)  # Debug: Print the full response to understand its structure
   
    # ADDITION: Safely capture inner JSON structure failures or out-of-quota messages sent via HTTP 200 blocks
    if "error" in response:
        print(f"Inner payload error encountered: {response['error'].get('message')}. Forcing fallback query routing...")
        time.sleep(2)
        return await fetch_probability(question, context, attempt=attempt + 1)
       
    output = response['choices'][0]['message']['content']
    print(output)
    return output








# Setup Dark Mode and Page Styling
ui.dark_mode().enable()
ui.query('body').style('background-color: #121212; color: white; font-family: Arial, sans-serif;')




# Global layout containers
with ui.column().classes('w-full max-w-2xl mx-auto p-8 mt-12'):
    ui.image('https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnRncnp0OTdmcHlpMjNmZ2g1eGl1ZXFjaDYxc2Q3bTVuaTJwMzZzZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3I05kogbcajmzchPdl/giphy.gif').classes('absolute inset-0 object-cover opacity-30 z-[-1]' )
    ui.label('Pondering The Orb').classes('animated-rainbow text-8xl font-bold mb-2 z-[1]' ).style('font-family: mythshire; color: #b8faff;')
    ui.label('Type in any question and provide context for said question, and a statistical probability for said question will occur.').classes('animated-rainbow-small text-lg text-blue-400 mb-6 tracking-wider z-[1]').style('color: #6bdbfa;')


    question_input = ui.input(label='Your Question').classes('w-full mb-4')
    context_input = ui.textarea(label='Context / Background Data').classes('w-full mb-6').props('rows=4')
   
    with ui.card().classes('w-full p-6 bg-gray-800 text-white mt-4') as result_card:
        result_text = ui.label('').classes('text-lg font-medium whitespace-pre-line')
   
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
            # ADDITION: Clear visual fallback display error binding directly onto NiceGUI frame layers
            result_text.set_text(f"⚠️ App Operation Failure:\n\n{ex}")
            result_card.set_visibility(True)
        finally:
            submit_btn.enable()
            spinner.set_visibility(False)
    submit_btn = ui.button('Calculate Probability', on_click=on_submit).classes('w-full bg-black text-white py-3 mt-4').style('border-radius: 8px;')


# Run the app
ui.run(title="Statistical AI", port=8080, host='0.0.0.0')