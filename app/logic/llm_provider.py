"""
LLM provider for Ollama using LangChain ChatOllama.
Uses LangChain's ChatOllama integration for local LLM inference.
"""
import os
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
                 temperature: float = 0.7, num_predict: int = 4096):
        """
        Initialize Ollama provider using LangChain ChatOllama.
        
        Follows LangChain documentation: https://python.langchain.com/docs/integrations/chat/ollama
        
        Args:
            model: Model name (e.g., "phi", "llama2", "llama3", "mistral", "llama3.2:1b")
            base_url: Ollama API base URL (default: "http://localhost:11434")
            temperature: Temperature for generation (default: 0.7)
            num_predict: Maximum number of tokens to generate (default: 4096)
        """
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=model,
                base_url=base_url,
                temperature=temperature,
                num_predict=num_predict,  # Allow longer responses
            )
        except ImportError:
            raise ImportError(
                "langchain-ollama library required. Install with: pip install langchain-ollama"
            )
        
        self.model = model
        self.base_url = base_url
        self.num_predict = num_predict
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using LangChain ChatOllama.
        
        Uses LangChain's message format with SystemMessage and HumanMessage,
        then invokes the LLM as documented in LangChain docs.
        """
        try:
            from langchain.messages import HumanMessage, SystemMessage
            
            # Create messages with system prompt and user prompt
            messages = [
                SystemMessage(content="You are a helpful educational assistant. Return only valid JSON when asked for structured data."),
                HumanMessage(content=prompt)
            ]
            
            # Invoke the LLM (as per LangChain documentation)
            response = self.llm.invoke(messages)
            
            # Extract content from response
            return response.content.strip() if response.content else ""
            
        except ImportError:
            # Fallback for older LangChain versions
            try:
                from langchain.schema.messages import HumanMessage, SystemMessage  # type: ignore
                messages = [
                    SystemMessage(content="You are a helpful educational assistant. Return only valid JSON when asked for structured data."),
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
    - OLLAMA_NUM_PREDICT: Maximum tokens to generate (default: 4096)
    
    Returns:
        OllamaProvider instance
    """
    model = os.getenv("OLLAMA_MODEL", "llama2")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "4096"))
    
    return OllamaProvider(model=model, base_url=base_url, temperature=temperature, num_predict=num_predict)
