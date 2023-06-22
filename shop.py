import openai
from dotenv import load_dotenv
load_dotenv(".gitignore/secrets.sh")
import os

def get_paint_info(color_prompts):
    # define OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key
    
    responses = []
    
    for prompt in color_prompts:
        messages = [
            {"role": "system", "content": "You are a customer in a paint store."},
            {"role": "user", "content": prompt}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        
        responses.append(response)
    
    return [response['choices'][0]['message']['content'] for response in responses]




