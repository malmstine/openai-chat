import os

import openai

token = os.environ.get("OPENAI_KEY")
openai.api_key = token


def send_messages(messages):
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    return res["choices"][0]["message"]["content"]

