from openai import AsyncOpenAI
from openai_chat.settings import settings


client = AsyncOpenAI(
    api_key=settings.OPENAI_KEY
)


async def send_messages(messages, model):
    return await client.chat.completions.create(model=model, messages=messages)
