from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# MODEL = "gpt-4o-mini"
MODEL = "o3-mini"

def get_openai_client():
    return OpenAI()

def get_openai_model():
    return MODEL