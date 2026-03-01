import os

from langchain_ollama import ChatOllama

model = os.environ.get("OLLAMA_MODEL", "qwen3:4b-instruct-2507-q4_K_M")

llm = ChatOllama(
    model=model,
    temperature=0.7,
    base_url="http://host.docker.internal:11434",
)