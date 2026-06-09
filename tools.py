import json
import datetime


def get_current_datetime(_=None) -> str:
 
    now = datetime.datetime.now()
    return json.dumps({
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M:%S"),
        "timezone": "Local Server Time"
    })



TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Retrieves the current date and time. Use this when the user asks about today's date, the current time, or relative time questions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Mapping dictionary for the execution engine
TOOL_REGISTRY = {
    "get_current_datetime": get_current_datetime
}
