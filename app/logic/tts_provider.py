"""
TTS (Text-to-Speech) provider abstraction for local TTS engines.
Supports Piper (preferred) and Coqui TTS as fallback.
"""
import os
import io
from typing import Optional, Tuple
from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    def synthesize(self, text: str, voice: str = "default") -> Tuple[bytes, str]:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to convert to speech
            voice: Voice name/identifier
            
        Returns:
            Tuple of (audio_bytes, mime_type)
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the TTS provider is available."""
        pass


class PiperProvider(TTSProvider):
    """Piper TTS provider - lightweight and fast local TTS."""
    
    def __init__(self, model_path: Optional[str] = None, voice: str = "en_US-lessac-medium"):
        """
        Initialize Piper provider.
        
        Args:
            model_path: Path to Piper model directory (if None, uses default location)
            voice: Voice name (default: "en_US-lessac-medium")
        """
        self.model_path = model_path
        self.default_voice = voice
        self._available = False
        self._use_python_api = False
        self._check_availability()
    
    def _check_availability(self):
        """Check if Piper is available (Python API or command-line)."""
        # Try Python API first
        try:
            import piper
            from piper import PiperVoice
            self._available = True
            self._use_python_api = True
            return
        except ImportError:
            pass
        
        # Try command-line tool
        try:
            import subprocess
            result = subprocess.run(
                ["piper", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                self._available = True
                self._use_python_api = False
                return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        self._available = False
    
    def is_available(self) -> bool:
        """Check if Piper is available."""
        return self._available
    
    def synthesize(self, text: str, voice: str = "default") -> Tuple[bytes, str]:
        """
        Synthesize text to speech using Piper.
        
        Args:
            text: Text to convert to speech
            voice: Voice name (uses default if "default")
            
        Returns:
            Tuple of (audio_bytes, mime_type)
        """
        if not self._available:
            raise RuntimeError(
                "Piper TTS is not installed. "
                "Install with: pip install piper-tts "
                "or install piper command-line tool from https://github.com/rhasspy/piper"
            )
        
        # Use default voice if specified
        if voice == "default":
            voice = self.default_voice
        
        try:
            if self._use_python_api:
                return self._synthesize_python_api(text, voice)
            else:
                return self._synthesize_cli(text, voice)
        except Exception as e:
            raise RuntimeError(f"Piper TTS synthesis failed: {str(e)}")
    
    def _synthesize_python_api(self, text: str, voice: str) -> Tuple[bytes, str]:
        """Synthesize using Python API."""
        import piper
        from piper import PiperVoice
        from piper.download import ensure_voice_exists
        
        # Ensure voice exists (downloads if needed)
        voice_path = ensure_voice_exists(voice, [])
        
        # Load voice
        voice_model = PiperVoice.load(voice_path)
        
        # Synthesize
        audio_stream = io.BytesIO()
        voice_model.synthesize(text, audio_stream)
        audio_bytes = audio_stream.getvalue()
        
        return audio_bytes, "audio/wav"
    
    def _synthesize_cli(self, text: str, voice: str) -> Tuple[bytes, str]:
        """Synthesize using command-line tool (fallback if Python API not available)."""
        # Note: This is a fallback. For best results, use the Python API.
        # Command-line piper requires model files to be manually downloaded.
        raise RuntimeError(
            "Piper command-line tool requires manual model setup. "
            "For easier setup, use the Python API: pip install piper-tts"
        )


class CoquiTTSProvider(TTSProvider):
    """Coqui TTS provider - alternative local TTS option."""
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        """
        Initialize Coqui TTS provider.
        
        Args:
            model_name: Model name for Coqui TTS
        """
        self.model_name = model_name
        self._tts = None
        self._available = False
        self._check_availability()
    
    def _check_availability(self):
        """Check if Coqui TTS is available."""
        try:
            from TTS.api import TTS
            self._available = True
        except ImportError:
            self._available = False
    
    def is_available(self) -> bool:
        """Check if Coqui TTS is available."""
        return self._available
    
    def synthesize(self, text: str, voice: str = "default") -> Tuple[bytes, str]:
        """
        Synthesize text to speech using Coqui TTS.
        
        Args:
            text: Text to convert to speech
            voice: Voice name (not used for Coqui, uses model default)
            
        Returns:
            Tuple of (audio_bytes, mime_type)
        """
        if not self._available:
            raise RuntimeError("Coqui TTS is not installed. Install with: pip install TTS")
        
        try:
            from TTS.api import TTS
            import numpy as np
            import soundfile as sf
            import io
            
            # Initialize TTS if not already done
            if self._tts is None:
                self._tts = TTS(model_name=self.model_name, progress_bar=False)
            
            # Synthesize
            wav = self._tts.tts(text)
            
            # Convert to bytes
            audio_stream = io.BytesIO()
            sf.write(audio_stream, np.array(wav), self._tts.synthesizer.output_sample_rate, format='WAV')
            audio_bytes = audio_stream.getvalue()
            
            return audio_bytes, "audio/wav"
            
        except Exception as e:
            raise RuntimeError(f"Coqui TTS synthesis failed: {str(e)}")


class NoTTSProvider(TTSProvider):
    """Fallback provider when no TTS is available."""
    
    def is_available(self) -> bool:
        return False
    
    def synthesize(self, text: str, voice: str = "default") -> Tuple[bytes, str]:
        raise RuntimeError(
            "No TTS provider is available. "
            "Install Piper TTS: pip install piper-tts "
            "or Coqui TTS: pip install TTS"
        )


def get_tts_provider() -> TTSProvider:
    """
    Factory function to get TTS provider based on availability and preferences.
    
    Priority:
    1. Piper (if available) - lightweight, fast
    2. Coqui TTS (if available) - alternative
    3. NoTTSProvider (fallback)
    
    Environment variables:
    - TTS_PROVIDER: "piper", "coqui", or "auto" (default: "auto")
    - PIPER_VOICE: Voice name for Piper (default: "en_US-lessac-medium")
    - COQUI_MODEL: Model name for Coqui TTS
    
    Returns:
        TTSProvider instance
    """
    provider_type = os.getenv("TTS_PROVIDER", "auto").lower()
    
    # Try Piper first (preferred)
    if provider_type in ("auto", "piper"):
        piper_provider = PiperProvider(
            voice=os.getenv("PIPER_VOICE", "en_US-lessac-medium")
        )
        if piper_provider.is_available():
            return piper_provider
    
    # Try Coqui TTS as fallback
    if provider_type in ("auto", "coqui"):
        coqui_provider = CoquiTTSProvider(
            model_name=os.getenv("COQUI_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
        )
        if coqui_provider.is_available():
            return coqui_provider
    
    # If specific provider requested but not available
    if provider_type == "piper":
        raise RuntimeError("Piper TTS requested but not installed. Install with: pip install piper-tts")
    if provider_type == "coqui":
        raise RuntimeError("Coqui TTS requested but not installed. Install with: pip install TTS")
    
    # Fallback to no-op provider
    return NoTTSProvider()

