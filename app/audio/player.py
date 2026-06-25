import subprocess
import pygame
import os
import threading
import queue
import sys
import re

sys.path.append(r"C:\AI EVO (Journey)\EVO - rebirth\app")

from utils.logger import setup_logger

# Initialize logger
logger = setup_logger("speaker")

# Initialize pygame mixer
pygame.init()
pygame.mixer.init()

# Audio queue
audio_queue = queue.Queue()

# Ensure audio folder exists
os.makedirs("audio", exist_ok=True)


def text_cleaner(text: str):
    return (
        text.replace("'", "'")
        .replace("\n", " ")
        .replace("  ", " ")
        .replace("Mr.", "Mr·")   # protect before split
        .replace("Mrs.", "Mrs·")
        .replace("Dr.", "Dr·")
        .replace("Ms.", "Ms·")
        .strip()
    )


def chunkinizer(text, min_words=4):
    text = text_cleaner(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.replace("Mr·", "Mr.").replace("Mrs·", "Mrs.")
                  .replace("Dr·", "Dr.").replace("Ms·", "Ms.").strip()
                 for s in sentences if s.strip()]

    chunks = []
    buffer = ""

    for sentence in sentences:
        word_count = len(sentence.split())

        # Small sentence → merge with previous
        if word_count <= min_words:
            if chunks:
                chunks[-1] += " " + sentence
            else:
                buffer += " " + sentence

        else:
            if buffer:
                sentence = buffer.strip() + " " + sentence
                buffer = ""

            chunks.append(sentence)

    # Final buffer handling
    if buffer:
        if chunks:
            chunks[-1] += " " + buffer.strip()
        else:
            chunks.append(buffer.strip())

    logger.info(f"Split text into {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        logger.info(f"Chunk {i}: {chunk}")

    return chunks


def producer(chunks):
    """
    Generates TTS audio files asynchronously.
    """

    logger.info("Producer started")

    voice = "en-US-AndrewMultilingualNeural"

    for i, chunk in enumerate(chunks):
        path = f"audio/chunk_{i}.mp3"

        logger.info(f"Generating audio for chunk {i}")

        try:
            with open("terminal.log", "a", encoding="utf-8") as f:

                subprocess.run(
                    [
                        "edge-tts",
                        "--voice", voice,
                        "--text", chunk,
                        "--write-media", path,
                        "--rate=-7%",
                        "--pitch=-7Hz"
                    ],
                    stdout=f,
                    stderr=f,
                    check=True
                )

            logger.info(f"Saved audio: {path}")

            audio_queue.put(path)

        except subprocess.CalledProcessError as e:
            logger.error(f"edge-tts failed for chunk {i}: {e}")

        except Exception as e:
            logger.error(f"Unexpected producer error: {e}")

    logger.info("Producer finished")

    # Stop signal
    audio_queue.put(None)


def consumer():
    """
    Plays generated audio files sequentially.
    """

    logger.info("Consumer started")

    while True:
        path = audio_queue.get()

        if path is None:
            logger.info("Consumer received stop signal")
            break

        try:
            logger.info(f"Playing: {path}")

            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        except Exception as e:
            logger.error(f"Playback error for {path}: {e}")

    logger.info("Consumer finished")


def cleanup_audio():
    """
    Removes old generated audio files.
    """

    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        for file in os.listdir("audio"):
            if file.endswith(".mp3"):
                os.remove(os.path.join("audio", file))

        logger.info("Cleaned old audio files")

    except Exception as e:
        logger.error(f"Cleanup error: {e}")


def speak(text):
    """
    Main TTS pipeline.
    """

    logger.info("Speak started")

    cleanup_audio()

    chunks = chunkinizer(text)

    producer_thread = threading.Thread(
        target=producer,
        args=(chunks,),
        daemon=True
    )

    producer_thread.start()

    consumer()

    producer_thread.join()

    logger.info("Speak finished")


if __name__ == "__main__":

    demo_text = "Good evening, Mr. Jain. It's 9:02 PM on Sunday, May 10th. I'm ready to assist you—whether you need to check your JEE study schedule, manage your smart home devices, or anything else. How can I help you tonight?"

    speak(demo_text)