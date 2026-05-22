# BACKEND CODE - Pure business logic and AI integration

def analyze_document(text: str):
    """Core AI analysis - This is the BACKEND intelligence"""
    
    system_prompt = "You are an expert document analyst..."  # ← AI instructions
    
    response = client.chat.completions.create(  # ← Call external API
        model="deepseek-chat",
        messages=[...]
    )
    
    return response.choices[0].message.content  # ← Return to caller