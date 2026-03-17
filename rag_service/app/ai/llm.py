import os

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

# LLM Provider selection: "ollama" or "openrouter" (or any OpenAI-compatible API)
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()

# Ollama settings
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:4b-instruct-2507-q4_K_M")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

# OpenRouter / OpenAI-compatible API settings
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Common settings
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))


if LLM_PROVIDER == "openrouter":
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is required when LLM_PROVIDER is 'openrouter'. "
            "Please set it in your .env file. Get your API key from https://openrouter.ai"
        )
    llm = ChatOpenAI(
        model=OPENROUTER_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )
else:
    # Default to Ollama
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=LLM_TEMPERATURE,
        base_url=OLLAMA_BASE_URL,
    )