from services.bedrock_llm import call_llm
from services.date_parser import extract_datetime
import os
import pandas as pd

EXCEL_PATH = "appointments.xlsx"

def detect_intent_node(state):
    user_input = state.user_input
    response = call_llm(f"Classify user intent: '{user_input}'\nRespond with 'general' or 'booking'")
    intent = "booking" if "booking" in response.lower() else "general"
    return {"intent": intent}

def general_query_node(state):
    user_input = state.user_input
    response = call_llm(f"Answer this general question briefly: {user_input}")
    print("Bot:", response)
    return {}  # No state change

def extract_datetime_node(state):
    user_input = state.user_input
    datetime_value = extract_datetime(user_input)
    if datetime_value:
        print(f"Bot: Got it. Noted your preference for {datetime_value}.")
        return {"datetime": datetime_value}
    else:
        print("Bot: Could you please specify the date and time?")
        return {}  # Let fallback handle missing datetime

def fallback_node(state):
    user_input = input("User: ")
    return {"user_input": user_input}

def mode_selection_node(state):
    print("Bot: Do you prefer a Virtual or Telephonic appointment?")
    mode_input = input("User: ").strip().lower()
    if "virtual" in mode_input:
        return {"mode": "Virtual"}
    elif "phone" in mode_input or "tele" in mode_input:
        return {"mode": "Telephonic"}
    else:
        print("Bot: Sorry, I didn't catch that.")
        return {}  # Retry not built-in here, but could be handled via fallback

def confirmation_node(state):
    print(f"Bot: Confirming your {state.mode} appointment for {state.datetime}.")

    # Load Excel file or create empty one
    try:
        # Define more calendar-like columns
        columns = ["Date", "Day", "Time", "Mode", "Notes"]
        
        if os.path.exists(EXCEL_PATH):
            df = pd.read_excel(EXCEL_PATH)
            print(f"Debug: Loaded existing Excel file with {len(df)} records")
            # Make sure all expected columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
        else:
            df = pd.DataFrame(columns=columns)
            print("Debug: Created new DataFrame (Excel file not found)")

        # Parse date string to get components
        # Expected format like "Sunday 01:00 PM"
        date_parts = state.datetime.split()
        
        if len(date_parts) >= 2:
            day = date_parts[0]  # e.g., "Sunday"
            time = ' '.join(date_parts[1:])  # e.g., "01:00 PM"
            
            # For date, we'll use current date if it's for today/tomorrow, otherwise next occurrence
            import datetime
            today = datetime.datetime.now()
            
            # Calculate date based on day of week
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            current_day_idx = today.weekday()  # 0 for Monday
            target_day_idx = days_of_week.index(day)
            
            days_ahead = (target_day_idx - current_day_idx) % 7
            if days_ahead == 0:  # Same day
                days_ahead = 7  # Next week
                
            target_date = today + datetime.timedelta(days=days_ahead)
            formatted_date = target_date.strftime("%Y-%m-%d")  # e.g., "2025-06-15"
            
            # Check if the slot is already booked
            is_booked = any((df["Day"] == day) & (df["Time"] == time))

            if is_booked:
                print(f"Bot: Sorry, {state.datetime} is already booked. Please choose another time.")
                # Explicitly ask for a new time
                print("Bot: What other date and time would work for you?")
                new_time_input = input("User: ")
                # Process this new input immediately
                datetime_value = extract_datetime(new_time_input)
                if datetime_value:
                    print(f"Bot: Got it. Updated your preference to {datetime_value}.")
                    # Keep the same mode but update datetime
                    return {"datetime": datetime_value, "user_input": new_time_input}
                else:
                    print("Bot: I couldn't understand that time. Let's start over.")
                    return {"confirmed": False, "datetime": None, "mode": None}
            else:
                # Save the new booking in calendar format
                new_entry = {
                    "Date": formatted_date,
                    "Day": day,
                    "Time": time,
                    "Mode": state.mode,
                    "Notes": state.user_input
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                
                # Save with explicit error handling
                try:
                    # Sort by date and time for better calendar view
                    df["DateForSort"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors='coerce')
                    df = df.sort_values(by="DateForSort").drop(columns=["DateForSort"])
                    
                    df.to_excel(EXCEL_PATH, index=False)
                    print(f"Debug: Saved Excel file with {len(df)} records")
                    print("Bot: Your appointment has been saved.")
                except Exception as e:
                    print(f"Error saving appointment: {str(e)}")
                    print("Bot: There was a problem saving your appointment. Please try again.")
                
                return {"confirmed": True}
        else:
            print("Bot: There was an issue with the date/time format.")
            return {"confirmed": False}
    except Exception as e:
        print(f"Error in confirmation process: {str(e)}")
        print("Bot: Sorry, there was an issue with the booking system.")
        return {"confirmed": False}
