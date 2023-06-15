import openai
from dotenv import load_dotenv
load_dotenv(".gitignore/secrets.sh")
import os
import time


def get_paint_info(content):

    # define OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key

    #generate text
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
    #text prompt
        messages = [
            {"role": "user", "content": f"{content}"}
        ]    
    )

    # Pause execution to enforce rate limit
    time.sleep(2)  # Adjust the sleep duration as needed

    return completion.choices[0].message.content