import os
from nicegui import ui
from openai import AsyncOpenAI, AuthenticationError

# Read the environment variable directly from the terminal injection
client = AsyncOpenAI(
    base_url="https://openrouter.ai",
    api_key=os.environ.get("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")
)

async def fetch_probability(question: str, context: str):
    """Queries OpenRouter using a completely free open-source model."""
    try:
        if not os.environ.get("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"):
            return "Error: OPENAI_API_KEY could not be read. Please run using: OPENAI_API_KEY='your-key' python main.py"

        prompt = f"""
        Given the following context and question, provide a statistical probability (0% to 100%) 
        and a brief explanation based on the likelihood or truth of the statement.
        
        Context: {context}
        Question: {question}

        Format exactly as: "Probability: [X]%\nReasoning: [Explanation]"
        """
        
        response = await client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a precise statistical analysis AI."},
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "HTTP-Referer": "http://localhost:8080",
                "X-Title": "Statistical AI Project",
            }
        )
        return response.choices.message.content.strip()
        
    except AuthenticationError:
        return "Authentication Error: Your OpenRouter API key is incorrect or inactive."
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

# Setup Dark Mode and Page Styling
ui.dark_mode().enable()
ui.query('body').style('background-color: #121212; color: white; font-family: Arial, sans-serif;')

# Global layout containers
with ui.column().classes('w-full max-w-2xl mx-auto p-8 mt-12'):
    ui.label('Statistical AI Analyzer').classes('text-4xl font-bold mb-2 text-blue-500')
    ui.label('Powered by OpenRouter Free Tier').classes('text-sm text-gray-500 mb-6 uppercase tracking-wider')

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
        finally:
            submit_btn.enable()
            spinner.set_visibility(False)

    submit_btn = ui.button('Calculate Probability', on_click=on_submit).classes('w-full bg-blue-600 text-white py-3 mt-4').style('border-radius: 8px;')

# Run the app
ui.run(title="Statistical AI", port=8080, host='0.0.0.0')
