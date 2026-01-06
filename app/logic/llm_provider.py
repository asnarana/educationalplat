"""
LLM provider abstraction for pluggable model support.
Supports Ollama (local via LangChain ChatOllama), OpenAI, and HuggingFace.
"""
import os
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference using LangChain ChatOllama."""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama provider using LangChain ChatOllama.
        
        Args:
            model: Model name (e.g., "phi", "llama2", "mistral", "llama3.2:1b", "llama3.1")
            base_url: Ollama API base URL
        """
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=model,
                base_url=base_url,
                temperature=0.7,
            )
        except ImportError:
            raise ImportError(
                "langchain-ollama library required. Install with: pip install langchain-ollama"
            )
        
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using LangChain ChatOllama.
        Compatible with both old and new LangChain versions.
        """
        try:
            # Try new LangChain (>= 1.0) - langchain.messages
            try:
                from langchain.messages import HumanMessage, SystemMessage
                messages = [
                    SystemMessage(content="You are a helpful educational assistant. Return only valid JSON when asked for structured data."),
                    HumanMessage(content=prompt)
                ]
                response = self.llm.invoke(messages)
                return response.content.strip() if response.content else ""
            except ImportError:
                # Try old LangChain (< 1.0) - langchain.schema.messages
                try:
                    from langchain.schema.messages import HumanMessage, SystemMessage
                    messages = [
                        SystemMessage(content="You are a helpful educational assistant. Return only valid JSON when asked for structured data."),
                        HumanMessage(content=prompt)
                    ]
                    # Try invoke first (newer API)
                    if hasattr(self.llm, 'invoke'):
                        response = self.llm.invoke(messages)
                    elif hasattr(self.llm, 'predict_messages'):
                        response = self.llm.predict_messages(messages)
                    elif hasattr(self.llm, '__call__'):
                        response = self.llm(messages)
                    else:
                        # Fallback: use string prompt
                        system_prompt = "You are a helpful educational assistant. Return only valid JSON when asked for structured data.\n\n"
                        full_prompt = system_prompt + prompt
                        response = self.llm.predict(full_prompt) if hasattr(self.llm, 'predict') else self.llm(full_prompt)
                    
                    if hasattr(response, 'content'):
                        return response.content.strip() if response.content else ""
                    elif isinstance(response, str):
                        return response.strip()
                    else:
                        return str(response).strip()
                except ImportError:
                    # Last fallback: langchain.schema (very old versions)
                    try:
                        from langchain.schema import HumanMessage, SystemMessage
                        messages = [
                            SystemMessage(content="You are a helpful educational assistant. Return only valid JSON when asked for structured data."),
                            HumanMessage(content=prompt)
                        ]
                        if hasattr(self.llm, 'invoke'):
                            response = self.llm.invoke(messages)
                        elif hasattr(self.llm, 'predict_messages'):
                            response = self.llm.predict_messages(messages)
                        else:
                            response = self.llm(messages)
                        
                        if hasattr(response, 'content'):
                            return response.content.strip() if response.content else ""
                        elif isinstance(response, str):
                            return response.strip()
                        else:
                            return str(response).strip()
                    except ImportError:
                        # Absolute last resort: plain string prompt
                        system_prompt = "You are a helpful educational assistant. Return only valid JSON when asked for structured data.\n\n"
                        full_prompt = system_prompt + prompt
                        if hasattr(self.llm, 'predict'):
                            response = self.llm.predict(full_prompt)
                        elif hasattr(self.llm, '__call__'):
                            response = self.llm(full_prompt)
                        else:
                            raise RuntimeError("Unable to call LangChain ChatOllama with any known method")
                        return str(response).strip() if response else ""
        except Exception as e:
            raise RuntimeError(f"Ollama (LangChain ChatOllama) error: {str(e)}")


class OpenAIProvider(LLMProvider):
    """OpenAI provider for GPT models."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model name (e.g., "gpt-3.5-turbo", "gpt-4")
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("openai library required. Install with: pip install openai")
        
        if not self.client.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.model = model
    
    def generate(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful educational assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class HuggingFaceProvider(LLMProvider):
    """HuggingFace provider for hosted models."""
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.1", api_key: Optional[str] = None):
        """
        Initialize HuggingFace provider.
        
        Args:
            model: Model ID from HuggingFace
            api_key: HuggingFace API key (if None, reads from HUGGINGFACE_API_KEY env var)
        """
        try:
            from huggingface_hub import InferenceClient
            api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                raise ValueError("HuggingFace API key required. Set HUGGINGFACE_API_KEY environment variable.")
            self.client = InferenceClient(token=api_key)
        except ImportError:
            raise ImportError("huggingface_hub library required. Install with: pip install huggingface_hub")
        
        self.model = model
    
    def generate(self, prompt: str) -> str:
        """Generate response using HuggingFace Inference API."""
        try:
            response = self.client.text_generation(
                prompt=prompt,
                model=self.model,
                max_new_tokens=2000,
                temperature=0.7,
                top_p=0.9
            )
            return response
        except Exception as e:
            raise RuntimeError(f"HuggingFace API error: {str(e)}")


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get LLM provider based on environment variables.
    
    Environment variables:
    - LLM_PROVIDER: "ollama", "openai", or "huggingface" (default: "ollama")
    - OLLAMA_MODEL: Model name for Ollama (default: "llama2")
    - OLLAMA_BASE_URL: Ollama base URL (default: "http://localhost:11434")
    - OPENAI_API_KEY: API key for OpenAI (optional, paid)
    - OPENAI_MODEL: Model name for OpenAI (default: "gpt-3.5-turbo")
    - HUGGINGFACE_API_KEY: API key for HuggingFace (optional, paid)
    - HUGGINGFACE_MODEL: Model ID for HuggingFace
    
    Note: Ollama is free and runs locally. OpenAI and HuggingFace require API keys and may cost money.
    
    Returns:
        LLMProvider instance
    """
    provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if provider_type == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama2")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaProvider(model=model, base_url=base_url)
    
    elif provider_type == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAIProvider(model=model, api_key=api_key)
    
    elif provider_type == "huggingface":
        model = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        return HuggingFaceProvider(model=model, api_key=api_key)
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}. Use 'ollama', 'openai', or 'huggingface'")

