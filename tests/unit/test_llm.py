"""
Unit tests for LLM integration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os

from luanti_voyager.llm import OpenAILLM, AnthropicLLM, OllamaLLM, VoyagerLLM


class TestOpenAILLM:
    """Test OpenAI LLM integration"""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("openai.AsyncOpenAI")
    def test_openai_initialization(self, mock_client):
        """Test OpenAI LLM initializes correctly"""
        llm = OpenAILLM(model="gpt-4")
        
        assert llm.model == "gpt-4"
        mock_client.assert_called_once_with(api_key="test-key")
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})  
    @patch("openai.AsyncOpenAI")
    async def test_openai_generate(self, mock_client_class):
        """Test OpenAI generation"""
        # Setup mock
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Test
        llm = OpenAILLM()
        response = await llm.generate("Test prompt")
        
        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()
    
    def test_openai_missing_api_key(self):
        """Test OpenAI fails gracefully without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                OpenAILLM()


class TestAnthropicLLM:
    """Test Anthropic LLM integration"""
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("anthropic.AsyncAnthropic")
    def test_anthropic_initialization(self, mock_client):
        """Test Anthropic LLM initializes correctly"""
        llm = AnthropicLLM(model="claude-3-sonnet")
        
        assert llm.model == "claude-3-sonnet"
        mock_client.assert_called_once_with(api_key="test-key")
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("anthropic.AsyncAnthropic")
    async def test_anthropic_generate(self, mock_client_class):
        """Test Anthropic generation"""
        # Setup mock
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Test
        llm = AnthropicLLM()
        response = await llm.generate("Test prompt")
        
        assert response == "Test response"
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": "Test prompt"}],
            max_tokens=1000
        )
    
    def test_anthropic_missing_api_key(self):
        """Test Anthropic fails gracefully without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                AnthropicLLM()


class TestOllamaLLM:
    """Test Ollama LLM integration"""
    
    def test_ollama_initialization(self):
        """Test Ollama LLM initializes with defaults"""
        llm = OllamaLLM()
        
        assert llm.model == "llama3"
        assert llm.base_url == "http://localhost:11434"
    
    @patch.dict(os.environ, {"OLLAMA_MODEL": "codellama", "OLLAMA_BASE_URL": "http://custom:11434"})
    def test_ollama_env_vars(self):
        """Test Ollama respects environment variables"""
        llm = OllamaLLM()
        
        assert llm.model == "codellama"
        assert llm.base_url == "http://custom:11434"
    
    @patch("aiohttp.ClientSession")
    async def test_ollama_generate(self, mock_session_class):
        """Test Ollama generation"""
        # Setup mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "response": "Test response from Ollama"
        })
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_class.return_value = mock_session
        
        # Test
        llm = OllamaLLM(model="llama3.1:latest")
        response = await llm.generate("Test prompt")
        
        assert response == "Test response from Ollama"
        mock_session.post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1:latest",
                "prompt": "Test prompt",
                "stream": False
            }
        )
    
    @patch("aiohttp.ClientSession")
    async def test_ollama_error_handling(self, mock_session_class):
        """Test Ollama handles errors gracefully"""
        # Setup mock for error
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Model not found")
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_class.return_value = mock_session
        
        # Test
        llm = OllamaLLM()
        
        with pytest.raises(RuntimeError, match="Ollama request failed"):
            await llm.generate("Test prompt")


class TestVoyagerLLM:
    """Test VoyagerLLM wrapper"""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("openai.AsyncOpenAI")
    def test_voyager_llm_with_openai(self, mock_client):
        """Test VoyagerLLM with OpenAI provider"""
        llm = VoyagerLLM(provider="openai", model="gpt-4")
        
        assert llm.provider == "openai"
        assert isinstance(llm.llm, OpenAILLM)
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("anthropic.AsyncAnthropic") 
    def test_voyager_llm_with_anthropic(self, mock_client):
        """Test VoyagerLLM with Anthropic provider"""
        llm = VoyagerLLM(provider="anthropic", model="claude-3-sonnet")
        
        assert llm.provider == "anthropic"
        assert isinstance(llm.llm, AnthropicLLM)
    
    def test_voyager_llm_with_ollama(self):
        """Test VoyagerLLM with Ollama provider"""
        llm = VoyagerLLM(provider="ollama", model="codellama")
        
        assert llm.provider == "ollama"
        assert isinstance(llm.llm, OllamaLLM)
    
    def test_voyager_llm_invalid_provider(self):
        """Test VoyagerLLM raises error for invalid provider"""
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            VoyagerLLM(provider="invalid_provider")
    
    @patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "mistral"})
    def test_voyager_llm_from_env(self):
        """Test VoyagerLLM from environment variables"""
        llm = VoyagerLLM()
        
        assert llm.provider == "ollama"
        assert isinstance(llm.llm, OllamaLLM)


class TestLLMPromptFormatting:
    """Test prompt formatting and context handling"""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("openai.AsyncOpenAI")
    async def test_context_messages(self, mock_client_class):
        """Test LLM handles context messages correctly"""
        # Setup mock
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Context response"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Test
        llm = OpenAILLM()
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        response = await llm.generate("ignored", messages=messages)
        
        assert response == "Context response"
        
        # Verify messages were passed correctly
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["messages"] == messages