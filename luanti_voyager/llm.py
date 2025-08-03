"""
LLM integration for intelligent agent decision making.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM."""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI GPT integration."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
            
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package required: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from OpenAI."""
        try:
            messages = kwargs.get("messages")
            if messages is None:
                messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "ERROR: Failed to get LLM response"


class AnthropicLLM(BaseLLM):
    """Anthropic Claude integration."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
            
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic package required: pip install anthropic")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from Anthropic Claude."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return "ERROR: Failed to get LLM response"


class OllamaLLM(BaseLLM):
    """Ollama local LLM integration."""

    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        try:
            import aiohttp
            self.session = None  # Will be created in first request
        except ImportError:
            raise ImportError("aiohttp package required for Ollama: pip install aiohttp")
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            import aiohttp
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from Ollama."""
        try:
            session = await self._get_session()
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
            if "temperature" in kwargs or "max_tokens" in kwargs:
                payload["options"] = {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 1000),
                }
            
            response = await session.post(
                f"{self.base_url}/api/generate", json=payload
            )
            if response.status == 200:
                result = await response.json()
                return result.get("response", "")
            error_text = await response.text()
            logger.error(
                f"Ollama API error {response.status}: {error_text}"
            )
            raise RuntimeError("Ollama request failed")

        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            raise RuntimeError(
                f"Failed to connect to Ollama at {self.base_url}: {e}"
            ) from e
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()


class VoyagerLLM:
    """LLM interface for Voyager agent decision making."""

    def __init__(self, provider: Optional[str] = None, **kwargs):
        provider = provider or os.getenv("LLM_PROVIDER", "none")
        self.provider = provider
        self.llm: Optional[BaseLLM] = None
        
        if provider == "openai":
            self.llm = OpenAILLM(**kwargs)
        elif provider == "anthropic":
            self.llm = AnthropicLLM(**kwargs)
        elif provider == "ollama":
            self.llm = OllamaLLM(**kwargs)
        elif provider == "none":
            logger.info("LLM disabled - using basic exploration")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    async def close(self):
        """Close LLM connections."""
        if hasattr(self.llm, 'close'):
            await self.llm.close()
    
    async def decide_action(self, world_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Decide what action to take based on world state."""
        if not self.llm:
            return None  # Fall back to basic exploration
            
        prompt = self._build_decision_prompt(world_state)
        
        try:
            response = await self.llm.generate(prompt, max_tokens=500, temperature=0.3)
            return self._parse_action_response(response)
        except Exception as e:
            logger.error(f"LLM decision error: {e}")
            return None
    
    def _build_decision_prompt(self, state: Dict[str, Any]) -> str:
        """Build prompt for action decision."""
        agent_pos = state.get("agent_position", {})
        nearby_blocks = state.get("nearby_blocks", [])
        
        # Analyze nearby environment
        block_types = {}
        for block in nearby_blocks:
            block_type = block.get("type", "unknown")
            block_types[block_type] = block_types.get(block_type, 0) + 1
        
        # Create environment summary
        env_summary = []
        for block_type, count in sorted(block_types.items(), key=lambda x: x[1], reverse=True):
            if block_type != "ignore":  # Skip void blocks
                env_summary.append(f"{count}x {block_type}")
        
        prompt = f"""You are an AI agent exploring a Luanti (Minecraft-like) world.

CURRENT SITUATION:
- Position: x={agent_pos.get('x', 0):.1f}, y={agent_pos.get('y', 0):.1f}, z={agent_pos.get('z', 0):.1f}
- Health: {state.get('hp', 20)}/20 HP
- Nearby blocks: {', '.join(env_summary) if env_summary else 'mostly void/air'}
- Total blocks visible: {len(nearby_blocks)}

AVAILABLE ACTIONS:
1. move_to <x> <y> <z> - Walk to coordinates  
2. teleport <x> <y> <z> - Instant teleport
3. dig <x> <y> <z> - Mine block at coordinates
4. place <block_type> <x> <y> <z> - Place block
5. explore - Random exploration movement
6. wait - Stay in place

EXPLORATION GOALS:
- **SURVIVAL FIRST**: Monitor health - if low, prioritize safety over exploration
- Find interesting terrain features (caves, structures, ores)
- Collect valuable resources (wood, stone, ores) 
- Avoid getting stuck in void areas or dangerous situations
- Build simple structures for testing
- Map the world systematically

Choose ONE action that makes the most sense given the current situation.
Respond with ONLY a JSON object in this format:
{{"action": "move_to", "params": {{"x": 10, "y": 5, "z": -3}}, "reason": "Moving towards stone deposits"}}

Your response:"""
        
        return prompt
    
    def _parse_action_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response into action dict."""
        try:
            # Extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            action_data = json.loads(response)
            
            # Validate action format
            if "action" not in action_data:
                logger.warning("LLM response missing 'action' field")
                return None
                
            action_type = action_data["action"]
            params = action_data.get("params", {})
            reason = action_data.get("reason", "LLM decision")
            
            # Convert to agent action format
            if action_type == "move_to":
                return {
                    "type": "move",
                    "pos": params,
                    "reason": reason
                }
            elif action_type == "teleport":
                return {
                    "type": "teleport", 
                    "pos": params,
                    "reason": reason
                }
            elif action_type == "dig":
                return {
                    "type": "dig",
                    "pos": params,
                    "reason": reason
                }
            elif action_type == "place":
                return {
                    "type": "place",
                    "pos": params,
                    "block": params.get("block_type", "default:dirt"),
                    "reason": reason
                }
            elif action_type == "explore":
                return {
                    "type": "explore",
                    "reason": reason
                }
            elif action_type == "wait":
                return {
                    "type": "wait",
                    "reason": reason
                }
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return None
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            logger.warning(f"Response was: {response[:200]}...")
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None
    
    async def analyze_environment(self, state: Dict[str, Any]) -> str:
        """Generate analysis of current environment."""
        if not self.llm:
            return "Basic exploration mode (no LLM)"
            
        prompt = f"""Analyze this Luanti world environment data:
        
Agent Position: {state.get('agent_position', {})}
Nearby Blocks: {len(state.get('nearby_blocks', []))} blocks detected

Block Distribution:
{self._summarize_blocks(state.get('nearby_blocks', []))}

Provide a brief 2-3 sentence analysis of what the agent should focus on in this environment."""

        try:
            return await self.llm.generate(prompt, max_tokens=200, temperature=0.5)
        except Exception as e:
            logger.error(f"Environment analysis error: {e}")
            return f"Analysis failed: {e}"
    
    def _summarize_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        """Summarize block distribution."""
        block_counts = {}
        for block in blocks:
            block_type = block.get("type", "unknown")
            block_counts[block_type] = block_counts.get(block_type, 0) + 1
        
        summary = []
        for block_type, count in sorted(block_counts.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"  {block_type}: {count}")
        
        return "\n".join(summary) if summary else "  No blocks detected"