from audio.player import speak
from core.brain import chat, save_session  # export a save_session function
from audio.transcription import listen
from utils.logger import setup_logger
from utils.delete_audio import remove_audio_files

logger = setup_logger("main")

CYAN = "\033[96m"
DARK_BLUE = "\033[34m"
RESET = "\033[0m"

def main():
    logger.info("EVO Assistant started")

    while True:
        try:
            user_query = input(">>> ")

            if user_query.lower() in ["exit", "quit"]:
                logger.info("Shutting down assistant")
                save_session()  # save memory on clean exit
                break

            if not user_query:
                continue

            logger.info(f"User said: {user_query}")
            print(f"{CYAN}You: {user_query}{RESET}")

            ai_response = chat(user_query)
            print(f"{DARK_BLUE}EVO: {ai_response}{RESET}")
            logger.info(f"AI response: {ai_response}")
            speak(ai_response)

        except KeyboardInterrupt:
            logger.warning("Interrupted by user")
            save_session()  # save memory on crash/ctrl+c
            break

        except Exception as e:
            logger.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()