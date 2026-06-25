import json
from openai import OpenAI
import os
from utils.logger import setup_logger

logger = setup_logger("extractor_logs")

client = OpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference"
)

def extract_memories(conversation: list[dict]) -> dict:
    convo_text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation[-6:]])
    logger.info("Extracting memories from last 6 messages")

    response = client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """Extract memory-worthy information from this conversation.
Return ONLY valid JSON in this format:
{
  "profile": {"name": "...", "job": "...", "location": "..."},  
  "facts": ["fact1", "fact2"],
  "preferences": ["likes X", "dislikes Y"]
}
Only include fields that are actually mentioned. Return {} if nothing is found.
Do NOT include guesses."""
            },
            {"role": "user", "content": convo_text}
        ]
    )

    raw = response.choices[0].message.content.strip()
    try:
        parsed = json.loads(raw)
        logger.info(f"Memories extracted successfully: {list(parsed.keys())}")
        return parsed
    except json.JSONDecodeError:
        logger.warning("Failed to parse extracted memories as JSON, returning empty dict")
        return {}