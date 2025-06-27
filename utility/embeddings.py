import numpy as np
from langchain_openai import AzureOpenAIEmbeddings
from pydantic import SecretStr
import os
from dotenv import load_dotenv

load_dotenv()


def get_embedding(text: str) -> np.ndarray:
    """
    Generate an embedding for the given text using Azure OpenAI.

    Args:
        text (str): Input text.

    Returns:
        np.ndarray: Embedding vector.
    """
    embedder = AzureOpenAIEmbeddings(

        azure_endpoint=os.getenv("embedding_azure_endpoint"),
        api_key=SecretStr(os.getenv("embedding_openai_api_key") or ""),
        api_version=os.getenv("embedding_openai_api_version"),
        # deployment_name=os.getenv("embedding_deployment_name", "text-embedding-3-small" if os.getenv("embedding_deployment_name") is None else os.getenv("embedding_deployment_name"))
        model=os.getenv("embedding_model_name")
    )
    embedding = embedder.embed_query(text)
    return np.array(embedding, dtype='float32')
