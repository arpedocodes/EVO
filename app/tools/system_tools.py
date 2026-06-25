import subprocess
from openai import OpenAI
import sys
import os
import json

sys.path.append(r"C:\AI EVO (Journey)\EVO - rebirth\app")
from utils.logger import setup_logger

from dotenv import load_dotenv
load_dotenv()


logger = setup_logger("agent")

client = OpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference"
)
def verifyer(commands: list, user_intent: str):

    system_prompt = """
You are EVO-VERIFY.

You will receive:
- USER INTENT
- A LIST OF COMMANDS

Your job:
For each command, decide if it is SAFE, UNSAFE, or UNKNOWN based on the intent.

Rules:
- SAFE = matches intent and not dangerous beyond intent
- UNSAFE = unrelated or destructive
- UNKNOWN = unclear

Return ONLY valid JSON in this format:

{
  "results": [
    {
      "command": "...",
      "status": "SAFE|UNSAFE|UNKNOWN",
      "reason": "optional"
    }
  ]
}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps({
                "user_intent": user_intent,
                "commands": commands
            })
        }
    ]

    response = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=messages
    )

    return json.loads(response.choices[0].message.content)

def run_commands(user_intent: str, commands: list):

    verdict = verifyer(commands, user_intent)

    results = []

    for item in verdict["results"]:

        if item["status"] == "SAFE":

            result = subprocess.run(
                item["command"],
                shell=True,
                capture_output=True,
                text=True
            )

            results.append({
                "command": item["command"],
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            })

        else:
            results.append({
                "command": item["command"],
                "blocked_reason": item.get("reason", item["status"])
            })

    return results