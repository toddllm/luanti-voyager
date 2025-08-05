#!/usr/bin/env python3
"""
Minimal multi-agent example with LLM responses.
Shows how agents with different personalities respond to situations.
"""

import asyncio
from luanti_voyager.multi_agent import AgentProfile, AgentCommunication, MessagePriority
from luanti_voyager.llm import VoyagerLLM

async def multi_agent_with_llm():
    """Simple demo showing personality-based agent responses."""
    print("\n🤖 Multi-Agent LLM Demo - Different Personalities\n")
    
    # Create an explorer with adventurous personality
    explorer = AgentProfile(
        name="Scout",
        personality="adventurous and excitable",
        skills=["exploration", "discovery"],
        communication_style="enthusiastic"
    )
    
    # Create a builder with methodical personality  
    builder = AgentProfile(
        name="Constructor",
        personality="careful and methodical", 
        skills=["building", "planning"],
        communication_style="precise"
    )
    
    # Initialize LLM (using Ollama local model)
    llm = VoyagerLLM(provider="ollama", model="llama3.2")
    
    # Explorer discovers something
    discovery = "I found a massive underground cave with glowing crystals!"
    
    print(f"💎 Explorer discovers: {discovery}\n")
    
    # Get responses based on personalities
    explorer_prompt = f"{explorer.get_system_prompt()}\n\nYou discovered: {discovery}\nWhat do you tell your team? (Keep it under 20 words)"
    builder_prompt = f"{builder.get_system_prompt()}\n\nYour teammate discovered: {discovery}\nHow do you respond? (Keep it under 20 words)"
    
    print("Explorer's reaction:")
    explorer_response = await llm.generate(explorer_prompt)
    print(f"  Scout: {explorer_response}\n")
    
    print("Builder's response:")
    builder_response = await llm.generate(builder_prompt)  
    print(f"  Constructor: {builder_response}\n")
    
    # Simulate urgent situation
    print("🚨 Urgent situation: Monster approaching the base!\n")
    
    urgent_prompt_explorer = f"{explorer.get_system_prompt()}\n\nA monster is approaching the base! What's your immediate action? (10 words max)"
    urgent_prompt_builder = f"{builder.get_system_prompt()}\n\nA monster is approaching the base! What's your immediate action? (10 words max)"
    
    print("Different reactions based on personality:")
    explorer_urgent = await llm.generate(urgent_prompt_explorer)
    print(f"  Scout (adventurous): {explorer_urgent}")
    
    builder_urgent = await llm.generate(urgent_prompt_builder)
    print(f"  Constructor (methodical): {builder_urgent}")

if __name__ == "__main__":
    asyncio.run(multi_agent_with_llm())