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
        from piper import PiperVoice
        from pathlib import Path
        import os
        
        # Determine download directory (where piper stores voices)
        if os.name == "nt":  # Windows
            download_dir = Path(os.getenv("APPDATA", "")) / "piper" / "voices"
        else:  # Linux/Mac
            download_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        
        # Ensure download directory exists
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Look for voice files in download directory
        voice_path = None
        json_path = None
        
        # Try to find existing voice files in multiple locations
        # Note: JSON file can be either {voice}.json or {voice}.onnx.json
        search_locations = [
            # Standard download directory with subdirectory
            (download_dir / voice / f"{voice}.onnx", download_dir / voice / f"{voice}.json"),
            (download_dir / voice / f"{voice}.onnx", download_dir / voice / f"{voice}.onnx.json"),
            # Standard download directory without subdirectory
            (download_dir / f"{voice}.onnx", download_dir / f"{voice}.json"),
            (download_dir / f"{voice}.onnx", download_dir / f"{voice}.onnx.json"),
            # Project root (where download_voices sometimes puts files)
            (Path(".") / f"{voice}.onnx", Path(".") / f"{voice}.json"),
            (Path(".") / f"{voice}.onnx", Path(".") / f"{voice}.onnx.json"),
            # Home directory
            (Path.home() / f"{voice}.onnx", Path.home() / f"{voice}.json"),
            (Path.home() / f"{voice}.onnx", Path.home() / f"{voice}.onnx.json"),
        ]
        
        for onnx_file, json_file in search_locations:
            if onnx_file.exists():
                # If the specified json_file doesn't exist, try the alternative
                if not json_file.exists():
                    # Try .onnx.json if we were looking for .json
                    if json_file.suffix == '.json' and not json_file.name.endswith('.onnx.json'):
                        alt_json = json_file.parent / f"{voice}.onnx.json"
                        if alt_json.exists():
                            json_file = alt_json
                    # Try .json if we were looking for .onnx.json
                    elif json_file.name.endswith('.onnx.json'):
                        alt_json = json_file.parent / f"{voice}.json"
                        if alt_json.exists():
                            json_file = alt_json
                
                if json_file.exists():
                    voice_path = onnx_file
                    json_path = json_file
                    break
        
        # If voice not found, try to download it
        if voice_path is None or not voice_path.exists():
            try:
                import piper.download_voices
                # download_voice requires download_dir parameter
                piper.download_voices.download_voice(voice, download_dir)
                # After download, check again
                if (download_dir / voice / f"{voice}.onnx").exists():
                    voice_path = download_dir / voice / f"{voice}.onnx"
                    json_path = download_dir / voice / f"{voice}.json"
                elif (download_dir / f"{voice}.onnx").exists():
                    voice_path = download_dir / f"{voice}.onnx"
                    json_path = download_dir / f"{voice}.json"
            except Exception as e:
                raise RuntimeError(
                    f"Voice model '{voice}' not found and could not be downloaded. "
                    f"Error: {str(e)}. "
                    f"Try downloading manually: python -m piper.download_voices {voice}"
                )
        
        # Verify files exist
        if voice_path is None or not voice_path.exists():
            raise RuntimeError(
                f"Voice model '{voice}' not found. "
                f"Download using: python -m piper.download_voices {voice}"
            )
        
        if json_path is None or not json_path.exists():
            # Try both naming conventions: .json and .onnx.json
            json_path = voice_path.with_suffix('.json')
            if not json_path.exists():
                # Try .onnx.json extension
                json_path = voice_path.parent / f"{voice_path.stem}.onnx.json"
            
            if not json_path.exists():
                raise RuntimeError(
                    f"Voice config file not found for '{voice}'. "
                    f"Looked for: {voice_path.with_suffix('.json')} and {voice_path.parent / f'{voice_path.stem}.onnx.json'}"
                )
        
        # Load voice model
        voice_model = PiperVoice.load(str(voice_path), str(json_path))
        
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

