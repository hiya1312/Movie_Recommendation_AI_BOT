# speech.py
import os
import azure.cognitiveservices.speech as speechsdk
from config import SPEECH_KEY, SPEECH_REGION

def speech_to_text(audio_bytes: bytes) -> str:
    import tempfile
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    audio_config = speechsdk.AudioConfig(filename=tmp_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    result = recognizer.recognize_once()
    os.unlink(tmp_path)
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        raise RuntimeError(f"Speech cancelled: {details.reason} — {details.error_details}")
    return ""

def text_to_speech(text) -> bytes:
    config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )
    # audio_config=None prevents server-side playback; audio is returned as bytes instead
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)
    result = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data
    raise RuntimeError(f"TTS failed: {result.reason}")