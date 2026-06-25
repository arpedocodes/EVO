import subprocess
import sys
from pathlib import Path
import os
import platform
from utils.logger import setup_logger

logger = setup_logger("execute_code")

BLACKLISTED_DIRS_WINDOWS = [
    "C:\\Windows",
    "C:\\Windows\\System32",
    "C:\\Windows\\SysWOW64",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
    "C:\\Users\\Default",
    f"C:\\Users\\{os.getlogin()}\\AppData",
]

def get_blacklist():
    if platform.system() == "Windows":
        return BLACKLISTED_DIRS_WINDOWS
    return []

def execute_python(code: str) -> str:
    logger.info("Executing Python code")
    logger.debug(f"Code:\n{code}")

    try:
        sandbox_header = f"""
import builtins
from pathlib import Path

_original_open = builtins.open
_blacklist = {get_blacklist()}

def _safe_open(file, *args, **kwargs):
    resolved = str(Path(file).resolve()).lower()
    for blocked in _blacklist:
        if resolved.startswith(blocked.lower()):
            raise PermissionError(f"Access denied: {{file}} is a restricted path.")
    return _original_open(file, *args, **kwargs)

builtins.open = _safe_open
"""
        full_code = sandbox_header + code

        result = subprocess.run(
            [sys.executable, "-c", full_code],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr

        if result.returncode != 0:
            logger.error(f"Execution failed | return code: {result.returncode}\n{result.stderr}")
        else:
            logger.info("Execution successful")
            logger.debug(f"Output:\n{output}")

        return output if output.strip() else "[Executed successfully, no output]"

    except subprocess.TimeoutExpired:
        logger.error("Execution timed out after 30 seconds")
        return "[Error] Execution timed out after 30 seconds"

    except Exception as e:
        logger.exception(f"Unexpected error during execution: {e}")
        return f"[Error] Unexpected error: {str(e)}"