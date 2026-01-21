"""
LLM provider for Ollama using LangChain ChatOllama.
Uses LangChain's ChatOllama integration for local LLM inference.
"""
import os
import requests
from typing import Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference using LangChain ChatOllama."""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434", 
                 temperature: float = 0.7, num_predict: int = 3072, timeout: int = 120):
        """
        Initialize Ollama provider using LangChain ChatOllama.
        
        Follows LangChain documentation: https://python.langchain.com/docs/integrations/chat/ollama
        
        Args:
            model: Model name (e.g., "phi", "llama2", "llama3", "mistral", "llama3.2:1b")
            base_url: Ollama API base URL (default: "http://localhost:11434")
            temperature: Temperature for generation (default: 0.7)
            num_predict: Maximum number of tokens to generate (default: 3072, balanced for speed and completeness)
            timeout: Request timeout in seconds (default: 120)
        """
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=model,
                base_url=base_url,
                temperature=temperature,
                num_predict=num_predict,  # Reduced from 4096 for faster responses
                timeout=timeout,  # Add timeout
            )
        except ImportError:
            raise ImportError(
                "langchain-ollama library required. Install with: pip install langchain-ollama"
            )
        
        self.model = model
        self.base_url = base_url
        self.num_predict = num_predict
        self.timeout = timeout
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using LangChain ChatOllama.
        
        Uses LangChain's message format with SystemMessage and HumanMessage,
        then invokes the LLM as documented in LangChain docs.
        
        Includes connection check and timeout handling.
        """
        # First, verify Ollama is running and accessible
        try:
            health_check = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if health_check.status_code != 200:
                raise RuntimeError(f"Ollama is not responding. Status: {health_check.status_code}. Make sure Ollama is running at {self.base_url}")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running: 'ollama serve'")
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Ollama connection timeout. Make sure Ollama is running at {self.base_url}")
        
        # Check if model is available
        try:
            models_response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if models_response.status_code == 200:
                models_data = models_response.json()
                available_models = [m.get("name", "") for m in models_data.get("models", [])]
                
                # Check if model exists (with or without :latest tag)
                # Ollama stores models as "model:latest" but can be called with just "model"
                model_found = False
                for available_model in available_models:
                    # Check exact match or if available model starts with our model name
                    if available_model == self.model or available_model.startswith(self.model + ":"):
                        model_found = True
                        break
                    # Also check if our model name matches the base name (without tag)
                    if available_model.split(":")[0] == self.model:
                        model_found = True
                        break
                
                if not model_found:
                    raise RuntimeError(
                        f"Model '{self.model}' not found in Ollama. "
                        f"Available models: {', '.join(available_models) if available_models else 'none'}. "
                        f"Download with: 'ollama pull {self.model}'"
                    )
        except RuntimeError:
            # Re-raise RuntimeError (model not found)
            raise
        except Exception as e:
            # If we can't check models, continue anyway (might be a version issue)
            print(f"Warning: Could not verify model availability: {e}")
        
        try:
            from langchain.messages import HumanMessage, SystemMessage
            
            # Create messages with system prompt and user prompt
            messages = [
                SystemMessage(content="You are a JSON API. You MUST respond with ONLY valid JSON - no prose, no markdown, no text outside JSON."),
                HumanMessage(content=prompt)
            ]
            
            # Invoke the LLM with timeout (handled by ChatOllama timeout parameter)
            print(f"[DEBUG] Calling Ollama model '{self.model}' (timeout: {self.timeout}s, max tokens: {self.num_predict})...")
            response = self.llm.invoke(messages)
            
            # Extract content from response
            result = response.content.strip() if response.content else ""
            
            if not result:
                raise RuntimeError("LLM returned empty response. The model may not be responding correctly.")
            
            print(f"[DEBUG] LLM response received ({len(result)} chars)")
            return result
            
        except ImportError:
            # Fallback for older LangChain versions
            try:
                from langchain.schema.messages import HumanMessage, SystemMessage  # type: ignore
                messages = [
                    SystemMessage(content="You are a JSON API. You MUST respond with ONLY valid JSON - no prose, no markdown, no text outside JSON."),
                    HumanMessage(content=prompt)
                ]
                response = self.llm.invoke(messages)
                return response.content.strip() if response.content else ""
            except ImportError:
                raise ImportError(
                    "Unable to import messages from langchain.messages or langchain.schema.messages. "
                    "Please ensure LangChain is properly installed: pip install langchain langchain-ollama"
                )
        except Exception as e:
            raise RuntimeError(f"Ollama (LangChain ChatOllama) error: {str(e)}")


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get Ollama LLM provider.
    
    Environment variables:
    - OLLAMA_MODEL: Model name for Ollama (default: "llama2")
    - OLLAMA_BASE_URL: Ollama base URL (default: "http://localhost:11434")
    - OLLAMA_TEMPERATURE: Temperature for generation (default: 0.7)
    - OLLAMA_NUM_PREDICT: Maximum tokens to generate (default: 3072, balanced for speed and completeness)
    - OLLAMA_TIMEOUT: Request timeout in seconds (default: 120)
    
    Returns:
        OllamaProvider instance
    """
    model = os.getenv("OLLAMA_MODEL", "llama2")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "4096"))  # Higher limit to avoid truncation
    timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    
    return OllamaProvider(model=model, base_url=base_url, temperature=temperature, num_predict=num_predict, timeout=timeout)
