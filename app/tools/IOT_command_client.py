import requests

ESP32_IP = "192.168.31.220"  # change this

def process_command(device, action):
    if device not in ["fan", "dim_light", "ceiling_fan", "plug_switch_top", "bright_light","plug_switch_left"]:
        return "Invalid device name."
    
    channel = 0
    if device in ["fan","plug_switch_left"]:
        channel = 1
    elif device in ["bright_light","plug_switch_top"]:
        channel = 4
    elif device == "dim_light":
        channel = 2
    elif device == "ceiling_fan":
        channel = 3

    # print(f"Processing channel: {channel}")

    try:
        response = requests.get(
            f"http://{ESP32_IP}/cmd",
            params={"channel": str(channel), "action":action}
        )
        if response.text == "OK":
            return {"status":"Success","device":device,"action":action}
        elif response.text == "Already":
            return {"status": "already_in_requested_state", "device": device, "action": action, "message": f"{device} is already {action}"}
    except:
        return "Connection Failed" 

print(process_command("ceiling_fan","OFF"))