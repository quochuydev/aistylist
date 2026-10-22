import os

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
MODEL = "deepseek-chat"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # optional: without it looks come back without images
IMAGE_MODEL = "imagen-4.0-fast-generate-001"
