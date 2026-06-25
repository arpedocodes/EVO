TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "IOT_command",
            "description": "Controls room devices. Use exact device names only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "enum": ["fan", "dim_light", "ceiling_fan", "plug_switch_top", "bright_light", "plug_switch_left"]
                    },
                    "action": {
                        "type": "string",
                        "enum": ["ON", "OFF"]
                    }
                },
                "required": ["device", "action"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_tasks",
            "description": (
                "Execute multiple Windows system commands in order. "
                "Use this for opening apps, websites, files, and performing system operations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "description": "The user's goal in simplified form."
                    },
                    "commands": {
                        "type": "array",
                        "description": (
                            "Ordered list of Windows CMD or PowerShell commands "
                            "to achieve the user's intent."
                        ),
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["intent", "commands"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a new Google Calendar event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Event title."
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": "Start datetime in ISO format."
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": "End datetime in ISO format."
                    },
                    "description": {
                        "type": "string"
                    },
                    "location": {
                        "type": "string"
                    }
                },
                "required": [
                    "summary",
                    "start_datetime",
                    "end_datetime"
                ],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_upcoming_calendar_events",
            "description": "Get upcoming calendar events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "default": 10
                    }
                },
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_calendar_events",
            "description": "Search for calendar events by name or keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "update_calendar_event",
            "description": (
                "Update an existing calendar event. "
                "Provide the event name and a changes object "
                "containing only the fields that should be modified."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string",
                        "description": "Current event name."
                    },
                    "changes": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string"
                            },
                            "start_datetime": {
                                "type": "string"
                            },
                            "end_datetime": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "location": {
                                "type": "string"
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "required": [
                    "event_name",
                    "changes"
                ],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_calendar_event",
            "description": "Delete a calendar event by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string"
                    }
                },
                "required": ["event_name"],
                "additionalProperties": False
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "internet_scraper",
        "description": (
            "Search, extract, or crawl internet content and return a summarized result. "
            "Use 'search' for web searches, 'extract' for extracting content from a specific URL, "
            "and 'crawl' for crawling and gathering information from websites."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Search query, URL, or crawl target depending on the selected search_type."
                    )
                },
                "search_type": {
                    "type": "string",
                    "description": "Type of internet operation to perform.",
                    "enum": [
                        "search",
                        "extract",
                        "crawl"
                    ]
                }
            },
            "required": [
                "query",
                "search_type"
            ],
            "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": (
            "Execute Python code for file management tasks. "
            "Use this for any file operation including reading, writing, moving, copying, "
            "deleting, searching, duplicate detection, bulk operations, and directory scanning. "
            "Always handle exceptions in the code. For destructive operations, scan and report "
            "affected files first before executing the actual operation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": (
                        "Valid Python code to execute. "
                        "Use print() to return any output or results. "
                        "Always include try/except blocks. "
                        "Never hardcode restricted system paths."
                    )
                }
            },
            "required": ["code"],
            "additionalProperties": False
        }
    }
}   
]