from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Use stream_llm for regular text generation
stream_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True,
    tags=["stream"],
    # Try to enable usage tracking
    stream_usage=True,
)

# Use non_stream_llm for structured output (Pydantic models)
non_stream_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=False,  # Disable streaming for structured output
    tags=["non-stream"],
)  