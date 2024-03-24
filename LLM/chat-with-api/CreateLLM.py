
import os
from genai.extensions.langchain import LangChainChatInterface
from genai.schema import TextGenerationParameters, TextGenerationReturnOptions
from genai import Client, Credentials

def createLLM():
    api_key = os.getenv("GENAI_KEY")
    api_url = os.getenv("GENAI_API")

    creds = Credentials(api_key, api_endpoint=api_url)
    params = TextGenerationParameters(decoding_method="greedy", max_new_tokens=400)
    client = Client(credentials=creds)

    llm = LangChainChatInterface(client=client,
            model_id="meta-llama/llama-2-70b-chat", parameters=params)
    return llm
