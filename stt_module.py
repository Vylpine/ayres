from faster_whisper import WhisperModel
import tempfile
import wave
import os


class SpeechToText:
    def __init__(self, model_size="base"):
        # Options: tiny, base, small, medium, large
        self.model = WhisperModel(model_size, 
        device="cpu",
        compute_type="int8")

    def transcribe_bytes(self, audio_bytes, sample_rate=16000):
        # Save to temp WAV (Whisper expects a file)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            filename = tmp.name

        with wave.open(filename, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            f.writeframes(audio_bytes)

        # Transcribe
        segments, _ = self.model.transcribe(filename)

        text = " ".join([seg.text for seg in segments]).strip()

        os.remove(filename)

        return text