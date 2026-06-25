import subprocess
import json
import sys
import os
from datetime import datetime
from collections import deque
from openai import OpenAI
from dotenv import load_dotenv
from core.toolsconfig import TOOLS
sys.path.append(r"C:\AI EVO (Journey)\EVO - rebirth\app")
from utils.logger import setup_logger
from tools.IOT_command_client import process_command
from tools.system_tools import run_commands
from memory.memory import build_system_prompt, save_episode
from memory.extractor import extract_memories
from memory.memory import update_core_memory
import uuid
from tools.calendar_management import create_event,get_upcoming_events,find_events,update_event,delete_event
from tools.internet_scraper import internet_scraper
from tools.execute_code import execute_python as run_python
import os
import platform

def get_blacklist():
    if platform.system() == "Windows":
        return [
            "C:\\Windows",
            "C:\\Windows\\System32",
            "C:\\Windows\\SysWOW64",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\ProgramData",
            "C:\\Users\\Default",
            f"C:\\Users\\{os.getlogin()}\\AppData",
        ]
    elif platform.system() == "Linux":
        return [
            "/etc", "/sys", "/proc", "/boot",
            "/dev", "/root", "/bin", "/sbin",
            "/usr/bin", "/usr/sbin", "/lib",
            "/lib64", "/usr/lib", "/run", "/snap",
        ]

BASE_SYSTEM_PROMPT = f"""You are EVO — a system-level AI assistant with access to IoT controls, automation tools, and a Python interpreter for file management.

The user is Anshuman Jain from Uttar Pradesh, India. Always address him as "Mr. Jain".

You are execution-focused, not conversational. Prefer using tools over explanations.

You will receive system context with date, time, day, and timezone. Use it when needed.

Rules:
- Always use tools when available
- Break complex tasks into multiple tool calls if needed
- Retry with a corrected approach if a tool fails
- Never assume tool results without execution
- For file tasks, always write and execute Python code via the interpreter
- Never perform destructive file operations (delete, overwrite, move) without first showing Mr. Jain what will be affected and getting explicit confirmation
- Always handle exceptions in generated code and report errors clearly
- For large directory scans, summarize results — never dump raw output
- Prefer send2trash over permanent deletion
- Never access, modify, or execute anything inside restricted directories

Restricted directories (never touch these or anything inside them):
{chr(10).join(get_blacklist())}"""
load_dotenv()

logger = setup_logger("agent")

client = OpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference"
)

# ─────────────────────────────────────────────
# MEMORY
# ─────────────────────────────────────────────

history = deque(maxlen=30)
execution_memory = []
conversation = []  # full conversation for memory saving
session_id = str(uuid.uuid4())

# ─────────────────────────────────────────────
# CRASH HANDLER
# ─────────────────────────────────────────────

def save_session():
    if conversation:
        logger.info("Saving session to long-term memory")
        save_episode(conversation, session_id)
        memories = extract_memories(conversation)
        if memories:
            for fact in memories.get("facts", []):
                update_core_memory("facts", fact)
            for pref in memories.get("preferences", []):
                update_core_memory("preferences", pref)
            if memories.get("profile"):
                update_core_memory("profile", memories["profile"])
        logger.info("Session saved successfully")
    else:
        logger.info("No conversation to save")

# ─────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────

TOOL_REGISTRY = {}

def register_tool(name):
    def wrapper(func):
        TOOL_REGISTRY[name] = func
        return func
    return wrapper

# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────

@register_tool("execute_python")
def execute_python(args):
    return run_python(args["code"])

@register_tool("IOT_command")
def iot_tool(args):
    return process_command(args["device"], args["action"])


@register_tool("execute_tasks")
def execute_tasks_tool(args):
    return run_commands(args["intent"], args["commands"])


@register_tool("create_calendar_event")
def create_calendar_event_tool(args):
    return create_event(
        summary=args["summary"],
        start_datetime=args["start_datetime"],
        end_datetime=args["end_datetime"],
        description=args.get("description", ""),
        location=args.get("location", "")
    )


@register_tool("get_upcoming_calendar_events")
def get_upcoming_calendar_events_tool(args):
    return get_upcoming_events(
        max_results=args.get("max_results", 10)
    )


@register_tool("search_calendar_events")
def search_calendar_events_tool(args):
    return find_events(
        args["query"]
    )


@register_tool("update_calendar_event")
def update_calendar_event_tool(args):
    return update_event(
        event_name=args["event_name"],
        changes=args["changes"]
    )


@register_tool("delete_calendar_event")
def delete_calendar_event_tool(args):
    return delete_event(
        event_name=args["event_name"]
    )

@register_tool("internet_scraper")
def execute_internet_scraper(args):
    return internet_scraper(
        query=args["query"],
        search_type=args["search_type"]
    )

# ─────────────────────────────────────────────
# TOOL RUNNER
# ─────────────────────────────────────────────

def run_tool(name: str, args: dict):
    logger.info(f"Tool → {name} | args={args}")
    handler = TOOL_REGISTRY.get(name)
    if not handler:
        return {"success": False, "error": "Unknown tool"}
    try:
        result = handler(args)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Tool error → {name} | {e}")
        return {"success": False, "error": str(e)}

# ─────────────────────────────────────────────
# CONTEXT BUILDER
# ─────────────────────────────────────────────

def add_context(user: str) -> str:
    now = datetime.now()
    return f"""
[SYSTEM TIME]
{now.strftime('%Y-%m-%d %H:%M:%S')}
{now.strftime('%A')}
[/SYSTEM TIME]

USER:
{user}
"""

# ─────────────────────────────────────────────
# MAIN CHAT LOOP
# ─────────────────────────────────────────────

def chat(user_message: str):

    # Build memory-enriched system prompt
    system_prompt = build_system_prompt(BASE_SYSTEM_PROMPT, user_message)
    logger.info("System prompt built with memory context")

    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": add_context(user_message)}
    ]

    while True:
        response = client.chat.completions.create(
            model="openai/gpt-4.1",
            tools=TOOLS,
            messages=messages,
        )

        msg = response.choices[0].message

        # ───── TOOL CALL ─────
        if msg.tool_calls:
            messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = run_tool(name, args)

                logger.info(f"Tool result → {name} | {str(result)[:200]}")

                execution_memory.append({
                    "time": datetime.now().isoformat(),
                    "tool": name,
                    "args": args,
                    "result": result
                })

                if not result.get("success"):
                    messages.append({
                        "role": "system",
                        "content": f"""
TOOL FAILURE:
Tool: {name}
Error: {result.get('error')}

Retry with a corrected approach.
"""
                    })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            continue

        # ───── FINAL RESPONSE ─────
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": msg.content})

        # Track full conversation for memory
        conversation.append({"role": "user", "content": user_message})
        conversation.append({"role": "assistant", "content": msg.content})
        logger.info(f"Conversation length: {len(conversation)} messages")

        return msg.content

# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        print("\nAI:", chat(user_input), "\n")