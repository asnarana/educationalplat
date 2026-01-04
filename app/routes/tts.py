"""
Routes for Text-to-Speech (TTS) functionality.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from app.logic.tts_provider import get_tts_provider, TTSProvider, NoTTSProvider

router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    """Request model for TTS endpoint."""
    text: str
    voice: str = "default"


@router.post("")
def text_to_speech(
    request: TTSRequest,
):
    """
    Convert text to speech audio.
    
    Returns an audio file (WAV format) as the response.
    
    This endpoint is optional and requires a TTS provider to be installed:
    - Piper TTS (recommended): `pip install piper-tts`
    - Coqui TTS (alternative): `pip install TTS`
    
    If no TTS provider is installed, returns a 503 error.
    The core quiz functionality works without TTS.
    
    Args:
        request: TTS request with text and optional voice
        
    Returns:
        Audio file (WAV) as binary response
    """
    # Get TTS provider
    try:
        tts_provider = get_tts_provider()
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"TTS provider not available: {str(e)}. "
                   "Install Piper TTS: pip install piper-tts "
                   "or Coqui TTS: pip install TTS"
        )
    
    # Check if provider is available
    if isinstance(tts_provider, NoTTSProvider) or not tts_provider.is_available():
        raise HTTPException(
            status_code=503,
            detail="No TTS provider is installed. "
                   "Install Piper TTS: pip install piper-tts "
                   "or Coqui TTS: pip install TTS. "
                   "The core quiz functionality works without TTS."
        )
    
    # Validate input
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    # Limit text length to prevent abuse
    if len(request.text) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Text is too long. Maximum 5000 characters."
        )
    
    # Synthesize speech
    try:
        audio_bytes, mime_type = tts_provider.synthesize(
            text=request.text,
            voice=request.voice
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"TTS synthesis failed: {str(e)}"
        )
    
    # Return audio file
    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers={
            "Content-Disposition": "inline; filename=speech.wav",
            "Cache-Control": "no-cache"
        }
    )


@router.get("/status")
def tts_status():
    """
    Check TTS provider availability status.
    
    Returns information about which TTS provider is available.
    """
    try:
        tts_provider = get_tts_provider()
        available = tts_provider.is_available()
        
        provider_name = type(tts_provider).__name__.replace("Provider", "")
        
        return {
            "available": available,
            "provider": provider_name if available else "none",
            "message": "TTS is ready" if available else "No TTS provider installed"
        }
    except Exception as e:
        return {
            "available": False,
            "provider": "none",
            "message": f"Error checking TTS status: {str(e)}"
        }

