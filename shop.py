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


def send_message(message):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    }
    data = {
        'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'},
                     {'role': 'user', 'content': message}]
    }
    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    message = response_json['choices'][0]['message']['content']
    return message

