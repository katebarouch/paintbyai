import openai
from dotenv import load_dotenv
load_dotenv("secrets.sh")
import os


def get_paint_info(content):

    # define OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")

    #generate text
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
    #text prompt
        messages = [
            {"role": "user", "content": f"{content}"}
        ]    
    )

    #print URL
    return completion.choices[0].message.content