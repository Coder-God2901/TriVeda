import os
import datetime
import re
from typing import Dict, Any, Optional

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time_input(time_str: str) -> str:
    time_str = time_str.lower().strip().replace(' ', '')
    
    patterns = [
        (r'^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$', lambda m: _format_time_match(m)),
        (r'^(\d{1,2})[.:](\d{2})\s*(am|pm)?$', lambda m: _format_time_match(m)),
    ]
    
    for pattern, formatter in patterns:
        match = re.match(pattern, time_str)
        if match:
            return formatter(match)
    
    return time_str

def _format_time_match(match) -> str:
    hour = int(match.group(1))
    minute = match.group(2) if len(match.groups()) > 1 and match.group(2) else "00"
    ampm = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
    
    if not ampm:
        ampm = "AM" if hour < 12 or hour == 24 else "PM"
    
    return f"{hour:02d}:{minute} {ampm.upper()}"

def get_user_input_with_exit(prompt: str, required: bool = True, default: str = "") -> str:
    while True:
        if default:
            value = input(f"  {prompt} [{default}] (or 'menu' to return): ").strip()
        else:
            value = input(f"  {prompt} (or 'menu' to return): ").strip()
        
        if value.lower() in ['menu', 'exit', 'quit', 'main', 'back', 'done']:
            return "EXIT_COMMAND"
        
        if value or not required:
            return value
        print("This field is required.")