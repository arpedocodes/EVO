from faster_whisper import WhisperModel
from audio.recorder import record
from utils.logger import setup_logger
import os
import torch
import noisereduce as nr
import soundfile as sf
import numpy as np
from pydub import AudioSegment

logger = setup_logger("stt")

# -----------------------------
# MODEL SETUP
# -----------------------------
def load_model():
    try:
        if torch.cuda.is_available():
            logger.info("Using GPU for Whisper")
            return WhisperModel("large-v3", device="cuda", compute_type="float16")
        else:
            logger.warning("GPU not available, falling back to CPU")
            return WhisperModel("base", device="cpu", compute_type="int8")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


model = load_model()


def preprocess_audio(input_path, output_path="data/output/output_clean.mp3"):
    # Load
    audio, sr = sf.read(input_path)
    
    # Noise reduction — uses first 0.5s as noise profile
    reduced = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75)
    
    # Normalize (boost volume to consistent level)
    max_val = np.max(np.abs(reduced))
    if max_val > 0:
        reduced = reduced / max_val * 0.95
    
    # Save as wav temporarily, export as mp3
    sf.write("data/output/temp_clean.wav", reduced, sr)
    segment = AudioSegment.from_wav("data/output/temp_clean.wav")
    segment = segment + 6  # boost by 6dB
    segment.export(output_path, format="mp3")
    
    logger.info("Audio preprocessed and cleaned")
    return output_path

# -----------------------------
# SPEECH TO TEXT
# -----------------------------
def STT(path_to_audio):
    if not os.path.exists(path_to_audio):
        logger.error(f"Audio file not found: {path_to_audio}")
        return ""

    logger.info(f"Transcribing: {path_to_audio}")

    try:
        segments, info = model.transcribe(
            path_to_audio,
            beam_size=5,
            language="z",
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        text = ""
        for segment in segments:
            logger.debug(f"Segment: {segment.text}")
            text += segment.text

        logger.info("Transcription complete")
        return text.strip()

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return ""


# -----------------------------
# LISTEN PIPELINE
# -----------------------------
def listen():
    logger.info("Listening pipeline started")

    try:
        print("\rListening...")
        record()
        print("\rRecorded!")
        
        audio_path = preprocess_audio("data/output/output.mp3")  # clean before STT
        
        text = STT(audio_path)
        print(f"\r{text}")
        logger.info(f"Final text: {text}")
        return text

    except Exception as e:
        logger.error(f"Listen pipeline failed: {e}")
        return ""