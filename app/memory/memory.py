import json
import chromadb
import os
import ollama
from datetime import datetime
from utils.logger import setup_logger
import subprocess
import time

logger = setup_logger("memory_logs")

core_memory_file_path = os.path.join(os.getcwd(), "app", "memory", "core_memory.json")

chroma_client = chromadb.PersistentClient(path="./memory_db")
episode_collection = chroma_client.get_or_create_collection("episodes")


def ensure_ollama_running():
    try:
        ollama.list()
        return True
    except Exception:

        try:
            logger.info("Running Ollama server.")
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            time.sleep(3)

            ollama.list()
            return True

        except Exception:
            return False

if not ensure_ollama_running():
    logger.error("Could not connect to Ollama.")

def retrieve_core_memory():
    if os.path.exists(core_memory_file_path):
        with open(core_memory_file_path, "r") as f:
            core_memory = json.load(f)
            logger.info("Core memory loaded successfully")
            return core_memory
    logger.warning("Core memory file not found, returning empty structure")
    return {"facts": [], "preferences": [], "profile": {}}

def save_core_memory(core_memory):
    with open(core_memory_file_path, "w") as f:
        json.dump(core_memory, f, indent=2)
    logger.info("Core memory saved successfully")

def update_core_memory(key: str, value: str):
    memory = retrieve_core_memory()
    if key == "facts":
        if value in memory["facts"]:
            logger.info(f"Fact already exists, skipping: {value}")
            return None
        memory["facts"].append(value)
        logger.info(f"New fact added: {value}")
    if key == "preferences":
        if value in memory["preferences"]:
            logger.info(f"Preference already exists, skipping: {value}")
            return None
        memory["preferences"].append(value)
        logger.info(f"New preference added: {value}")
    if key == "profile":
        if value in memory["profile"]:
            logger.info(f"Profile field already exists, skipping: {value}")
            return None
        memory["profile"].update(value)
        logger.info(f"Profile updated: {value}")
    save_core_memory(memory)

def save_episode(conversation: list[dict], session_id: str):
    logger.info(f"Saving episode for session: {session_id}")
    chats = "\n".join([f"{m['role']}: {m['content']}" for m in conversation])
    
    summary_response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": "Summarize this conversation. Extract key facts, decisions, and topics discussed. Be detailed."},
            {"role": "user", "content": chats}
        ]
    )
    summary = summary_response["message"]["content"]
    logger.info(f"Summary generated for session: {session_id}")

    episode_collection.add(
        documents=[summary],
        metadatas=[{"session_id": session_id, "timestamp": datetime.now().isoformat()}],
        ids=[session_id]
    )
    logger.info(f"Episode stored in ChromaDB: {session_id}")

def retrieve_relevant_episode(query: str, n_result=3) -> list[str]:
    if episode_collection.count() == 0:
        logger.info("No episodes in ChromaDB yet")
        return []
    results = episode_collection.query(query_texts=[query], n_results=min(n_result, episode_collection.count()))
    episodes = results["documents"][0] if results["documents"] else []
    logger.info(f"Retrieved {len(episodes)} relevant episodes for query")
    return episodes

def build_system_prompt(prompt: str, user_prompt: str):

    logger.info("Building system prompt with memory context")
    core = retrieve_core_memory()
    episodes = retrieve_relevant_episode(user_prompt)

    core_block = ""
    if core["profile"]:
        core_block += f"User Profile: {json.dumps(core['profile'])}\n"
    if core["facts"]:
        core_block += f"Known Facts: {'; '.join(core['facts'])}\n"
    if core["preferences"]:
        core_block += f"Preferences: {'; '.join(core['preferences'])}\n"

    episode_block = ""
    if episodes:
        episode_block = "Relevant Past Conversations:\n" + "\n---\n".join(episodes)

    prompt += f"\n\n{core_block}\n\n{episode_block}\nUse this memory naturally in conversation. Don't robotically list it — just be aware of it."
    logger.info("System prompt built successfully")
    return prompt

if __name__=="__main__":
    ensure_ollama_running()