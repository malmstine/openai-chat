import os

import openai

token = os.environ.get("OPENAI_KEY")
openai.api_key = token


def send_messages(messages):
    res = openai.ChatCompletion.create(model="gpt-4-1106-preview", messages=messages)
    return res["choices"][0]["message"]["content"]
