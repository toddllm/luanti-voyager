#!/usr/bin/env python3
"""
Test script for LLM integration with Luanti Voyager.
"""

import asyncio
import logging
import os
from pathlib import Path
from luanti_voyager.llm import VoyagerLLM

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not required, just helpful

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_llm_integration():
    """Test LLM integration with sample world state."""
    
    print("🧪 Testing Luanti Voyager LLM Integration")
    print("=" * 50)
    
    # Test with no LLM (basic mode)
    print("\n1. Testing basic mode (no LLM)...")
    basic_llm = VoyagerLLM(provider="none")
    
    sample_state = {
        "agent_position": {"x": 10.5, "y": 5.0, "z": -3.2},
        "nearby_blocks": [
            {"type": "default:stone", "pos": {"x": 10, "y": 4, "z": -3}},
            {"type": "default:dirt", "pos": {"x": 11, "y": 4, "z": -3}},
            {"type": "default:tree", "pos": {"x": 12, "y": 5, "z": -2}},
            {"type": "ignore", "pos": {"x": 9, "y": 6, "z": -4}}
        ],
        "inventory": {"default:stick": 2, "default:stone": 5},
        "hp": 20
    }
    
    action = await basic_llm.decide_action(sample_state)
    print(f"Basic mode action: {action}")
    
    # Test with OpenAI (if configured)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("\n2. Testing OpenAI integration...")
        try:
            openai_llm = VoyagerLLM(provider="openai")
            action = await openai_llm.decide_action(sample_state)
            print(f"OpenAI action: {action}")
            
            analysis = await openai_llm.analyze_environment(sample_state)
            print(f"OpenAI analysis: {analysis}")
        except Exception as e:
            print(f"OpenAI test failed: {e}")
    else:
        print("\n2. OpenAI test skipped (no OPENAI_API_KEY)")
    
    # Test with Anthropic (if configured)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("\n3. Testing Anthropic integration...")
        try:
            anthropic_llm = VoyagerLLM(provider="anthropic")
            action = await anthropic_llm.decide_action(sample_state)
            print(f"Anthropic action: {action}")
            
            analysis = await anthropic_llm.analyze_environment(sample_state)
            print(f"Anthropic analysis: {analysis}")
        except Exception as e:
            print(f"Anthropic test failed: {e}")
    else:
        print("\n3. Anthropic test skipped (no ANTHROPIC_API_KEY)")
    
    # Test with Ollama (local)
    print("\n4. Testing Ollama integration...")
    try:
        # Use available model explicitly
        ollama_llm = VoyagerLLM(provider="ollama", model="llama3.1:latest")
        action = await ollama_llm.decide_action(sample_state)
        print(f"Ollama action: {action}")
        
        analysis = await ollama_llm.analyze_environment(sample_state)
        print(f"Ollama analysis: {analysis}")
        
        # Close Ollama connection
        await ollama_llm.close()
    except Exception as e:
        print(f"Ollama test failed: {e}")
        print("Make sure Ollama is running: ollama serve")
    
    # Test void escape scenario
    print("\n5. Testing void escape scenario...")
    void_state = {
        "agent_position": {"x": 100, "y": 50, "z": 200},
        "nearby_blocks": [{"type": "ignore", "pos": {"x": i, "y": j, "z": k}} 
                         for i in range(95, 105) for j in range(45, 55) for k in range(195, 205)],
        "inventory": {},
        "hp": 20
    }
    
    # Test with Ollama for void escape (no API key needed)
    try:
        void_llm = VoyagerLLM(provider="ollama", model="llama3.1:latest")
        action = await void_llm.decide_action(void_state)
        print(f"Ollama void escape action: {action}")
        await void_llm.close()
    except Exception as e:
        print(f"Ollama void escape test failed: {e}")
    
    print("\n✅ LLM integration tests completed!")
    print("\nTo use with agent:")
    print("python -m luanti_voyager --llm ollama      # Local Ollama (recommended for dev)")
    print("python -m luanti_voyager --llm openai     # OpenAI GPT")
    print("python -m luanti_voyager --llm anthropic  # Anthropic Claude")
    print("\nFor API providers, set your keys:")
    print("export OPENAI_API_KEY=your_key_here")
    print("export ANTHROPIC_API_KEY=your_key_here")
    print("\nFor Ollama:")
    print("1. Install: https://ollama.ai/")
    print("2. Pull model: ollama pull llama3")
    print("3. Start server: ollama serve")


if __name__ == "__main__":
    asyncio.run(test_llm_integration())