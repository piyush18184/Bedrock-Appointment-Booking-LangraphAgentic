# from dateparser import parse

# def extract_datetime(text):
#     dt = parse(text)
#     return dt.strftime("%A %I:%M %p") if dt else None

from dateparser import parse
from services.bedrock_llm import call_llm
import json
import re

def extract_datetime(text):
    # Check if only day is provided without time
    day_only_patterns = [
        r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$',
        r'^next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)$',
        r'^(tomorrow|day after tomorrow)$'
    ]
    
    if any(re.match(pattern, text.lower()) for pattern in day_only_patterns):
        # Return special indicator that only day was provided
        return "TIME_MISSING"
    
    # First try with dateparser
    dt = parse(text)
    if dt:
        return dt.strftime("%A %I:%M %p")
    
    # If dateparser fails, use the LLM for more complex expressions
    prompt = f"""
    You are a sophisticated datetime extraction system. Extract the date and time from this text: "{text}"
    
    Key guidelines:
    1. For vague time references, use these standard interpretations:
       - "morning" = 9:00 AM
       - "afternoon" = 3:00 PM
       - "evening" = 6:00 PM
       - "night" = 8:00 PM
    
    2. For relative day references, calculate the actual day of week:
       - "tomorrow" = the day after today
       - "day after tomorrow" = two days from today
       - "next [day]" = the next occurrence of that day
    
    3. Be attentive to context clues that indicate both a date and time.
    
    4. Output format:
       - If both day and time are specified: "Day HH:MM AM/PM" (e.g., "Monday 03:00 PM")
       - If only a day is specified without time: "TIME_MISSING"
       - If no clear day and time can be identified: "None"
    
    Today is {parse('today').strftime('%A, %B %d, %Y')}.
    
    Respond ONLY with the formatted datetime string, "TIME_MISSING", or "None".
    """
    
    response = call_llm(prompt).strip()
    
    # Check for time missing indicator
    if response == "TIME_MISSING":
        return "TIME_MISSING"
    
    # Validate the response format (basic check)
    if response != "None" and ("AM" in response or "PM" in response):
        return response
    return None