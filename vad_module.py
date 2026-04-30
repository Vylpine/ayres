import webrtcvad
import numpy as np
from collections import deque
import wave
import time


class VoiceActivityDetector:
    def __init__(self, sample_rate=16000, frame_duration=20):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)

        self.vad = webrtcvad.Vad(3)

        # State
        self.speech_active = False
        self.speech_count = 0
        self.silence_count = 0
        self.buffer = []

        # Pre-buffer (~200ms)
        self.pre_buffer = deque(maxlen=10)

        # Thresholds
        self.start_threshold = 5
        self.end_threshold = 10
        self.energy_threshold = 500

        # Safety
        self.max_speech_seconds = 10
        self.speech_start_time = None

    def process_frame(self, frame_bytes):
        """
        Returns:
            None
            "start"
            "end"
        """

        # --- Always fill pre-buffer ---
        self.pre_buffer.append(frame_bytes)

        # --- Energy filter ---
        audio = np.frombuffer(frame_bytes, dtype=np.int16)
        energy = np.abs(audio).mean()

        if energy < self.energy_threshold:
            is_speech = False
        else:
            is_speech = self.vad.is_speech(frame_bytes, self.sample_rate)

        # --- Counters ---
        if is_speech:
            self.speech_count += 1
            self.silence_count = 0
        else:
            self.silence_count += 1

        # --- Start detection ---
        if not self.speech_active:
            if self.speech_count >= self.start_threshold:
                self.speech_active = True
                self.buffer = list(self.pre_buffer)  # include pre-roll
                self.speech_start_time = time.time()
                return "start"

        # --- While speaking ---
        if self.speech_active:
            self.buffer.append(frame_bytes)

            # Max duration safety
            if time.time() - self.speech_start_time > self.max_speech_seconds:
                return self._end_speech()

            # Normal end
            if self.silence_count >= self.end_threshold:
                return self._end_speech()

        return None

    def _end_speech(self):
        self.speech_active = False
        self.speech_count = 0
        self.silence_count = 0

        return "end"

    def get_audio(self):
        return b''.join(self.buffer)

    def save_audio(self, filename):
        audio_bytes = self.get_audio()

        with wave.open(filename, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)  # int16
            f.setframerate(self.sample_rate)
            f.writeframes(audio_bytes)