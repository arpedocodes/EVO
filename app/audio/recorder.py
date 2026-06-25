import sounddevice as sd
import numpy as np
from pydub import AudioSegment
import queue
import time
from utils.logger import setup_logger

logger = setup_logger("recorder")

SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
SILENCE_CHUNKS = 20

q = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    if status:
        logger.warning(f"Audio callback status: {status}")
    q.put(indata.copy())


def record_on_voice(threshold):
    logger.info(f"Listening... Threshold = {threshold}")

    recording = []
    speaking = False
    silence_counter = 0

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            blocksize=BLOCK_SIZE,
            callback=audio_callback
        ):
            while True:
                data = q.get()
                volume = np.linalg.norm(data) / len(data)

                # Optional debug
                # logger.debug(f"Volume: {volume}")

                if volume > threshold:
                    if not speaking:
                        logger.info("Recording started")
                        speaking = True
                    recording.append(data)
                    silence_counter = 0
                else:
                    if speaking:
                        recording.append(data)
                        silence_counter += 1

                if speaking and silence_counter > SILENCE_CHUNKS:
                    logger.info("Recording stopped due to silence")
                    break

    except Exception as e:
        logger.error(f"Error during recording: {e}")
        raise

    if not recording:
        logger.warning("No audio recorded")
        return None

    return np.concatenate(recording, axis=0)


def save_audio(audio):
    if audio is None:
        logger.error("No audio to save")
        return

    try:
        audio_int16 = np.int16(audio * 32767)

        segment = AudioSegment(
            audio_int16.tobytes(),
            frame_rate=SAMPLE_RATE,
            sample_width=2,
            channels=1
        )

        segment.export("data/output/output.mp3", format="mp3")
        logger.info("Saved audio to data/output/output.mp3")

    except Exception as e:
        logger.error(f"Error saving audio: {e}")


def record():
    logger.info("Record function started")

    threshold = 4e-05  # you may still need to tune this
    audio = record_on_voice(threshold)
    save_audio(audio)

    logger.info("Record function finished")

if __name__ == "__main__":
    record()
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("data/output/output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)