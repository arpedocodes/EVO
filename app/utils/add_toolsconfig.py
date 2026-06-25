import pprint
import importlib.util

def add_tool(name: str, description: str, args: dict, req: list):
    path = r"C:\AI EVO (Journey)\EVO - rebirth\app\core\toolsconfig.py"

    new_tool = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": args,
                "required": req,
                "additionalProperties": False
            }
        }
    }

    spec = importlib.util.spec_from_file_location("toolsconfig", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tools = module.TOOLS
    tools.append(new_tool)

    with open(path, "w", encoding="utf-8") as f:
        f.write("TOOLS = ")
        f.write(pprint.pformat(tools, width=120, sort_dicts=False))
        f.write("\n")

if __name__ == "__main__":
    add_tool()