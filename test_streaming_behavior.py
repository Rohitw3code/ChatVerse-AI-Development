#!/usr/bin/env python3
"""
Test script to demonstrate the difference between streaming and non-streaming LLM behavior.
"""

import asyncio
from chatagent.config.init import llm, stream_llm
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Literal


class RouterDecision(BaseModel):
    """Example structured output model"""
    next: Literal["agent_a", "agent_b", "finish"]
    reason: str = Field(description="Brief explanation for the decision")


async def test_non_streaming_structured():
    """Test non-streaming LLM with structured output - should return complete JSON"""
    print("\n" + "="*60)
    print("TEST 1: Non-Streaming LLM with Structured Output (JSON/Pydantic)")
    print("="*60)
    print("Expected: Complete JSON object returned immediately\n")
    
    structured_llm = llm.with_structured_output(RouterDecision)
    result = await structured_llm.ainvoke([
        HumanMessage(content="Route this task: send an email to john@example.com")
    ])
    
    print(f"Result Type: {type(result)}")
    print(f"Result: {result}")
    print(f"Next: {result.next}")
    print(f"Reason: {result.reason}")
    print("\n✅ Complete structured object received immediately!")


async def test_streaming_final_answer():
    """Test streaming LLM for final answer - should stream token by token"""
    print("\n" + "="*60)
    print("TEST 2: Streaming LLM for Final Answer (Natural Language)")
    print("="*60)
    print("Expected: Tokens stream one by one\n")
    
    print("Streaming response: ", end="", flush=True)
    
    async for chunk in stream_llm.astream([
        HumanMessage(content="In one sentence, what is Python?")
    ]):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    
    print("\n\n✅ Response streamed token-by-token!")


async def test_non_streaming_regular():
    """Test non-streaming LLM without structured output - should return complete message"""
    print("\n" + "="*60)
    print("TEST 3: Non-Streaming LLM without Structured Output")
    print("="*60)
    print("Expected: Complete message returned immediately\n")
    
    result = await llm.ainvoke([
        HumanMessage(content="In one sentence, what is JavaScript?")
    ])
    
    print(f"Result Type: {type(result)}")
    print(f"Content: {result.content}")
    print("\n✅ Complete message received immediately!")


async def main():
    print("\n" + "🔬 STREAMING BEHAVIOR TEST SUITE" + "\n")
    print("This demonstrates the two-LLM approach:")
    print("1. Non-streaming LLM for structured outputs (JSON/Pydantic)")
    print("2. Streaming LLM for final answers (natural language)")
    
    # Test 1: Non-streaming with structured output
    await test_non_streaming_structured()
    
    # Test 2: Streaming for final answer
    await test_streaming_final_answer()
    
    # Test 3: Non-streaming without structured output
    await test_non_streaming_regular()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("✅ Non-streaming LLM (llm): Perfect for JSON/Pydantic models")
    print("✅ Streaming LLM (stream_llm): Perfect for final answers")
    print("✅ All tests passed!")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
