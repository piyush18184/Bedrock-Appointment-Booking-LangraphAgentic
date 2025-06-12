import streamlit as st
from graph.state_machine import build_langgraph, AssistantState
import pandas as pd
import os
from services.date_parser import extract_datetime

# Page configuration
st.set_page_config(
    page_title="Appointment Booking Assistant",
    page_icon="📅",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_state" not in st.session_state:
    st.session_state.current_state = AssistantState(user_input="", intent="", datetime="", mode="", history=[])
if "waiting_for_input" not in st.session_state:
    st.session_state.waiting_for_input = False
if "input_context" not in st.session_state:
    st.session_state.input_context = None
if "graph" not in st.session_state:
    st.session_state.graph = build_langgraph()

# Sidebar with app info
with st.sidebar:
    st.title("📅 Appointment Assistant")
    st.markdown("""
    This assistant helps you book virtual or telephonic appointments.
    
    **Sample phrases to try:**
    - "I'd like to book an appointment"
    - "Schedule a meeting for Friday at 2pm"
    - "What services do you provide?"
    """)
    
    if st.button("View Appointment Calendar"):
        if os.path.exists("appointments.xlsx"):
            df = pd.read_excel("appointments.xlsx")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No appointments booked yet.")

# Main title
st.title("Appointment Booking Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Custom node handlers for Streamlit
def handle_datetime_extraction(state):
    user_input = state.user_input
    datetime_value = extract_datetime(user_input)
    
    if datetime_value == "TIME_MISSING":
        st.session_state.waiting_for_input = True
        st.session_state.input_context = "time_missing"
        st.session_state.messages.append({"role": "assistant", "content": "I see you've specified a day, but what time would you prefer?"})
        return None
    
    if datetime_value and datetime_value != "TIME_MISSING":
        st.session_state.messages.append({"role": "assistant", "content": f"Got it. Noted your preference for {datetime_value}."})
        return {"datetime": datetime_value}
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Could you please specify the date and time? For example, 'Monday at 3 PM' or 'next Friday at 10 AM'."})
        return {}

def handle_mode_selection(state):
    st.session_state.waiting_for_input = True
    st.session_state.input_context = "mode_selection"
    st.session_state.messages.append({"role": "assistant", "content": "Do you prefer a Virtual or Telephonic appointment?"})
    return None

def handle_confirmation(state):
    # Modified confirmation logic for Streamlit
    confirmation_msg = f"Confirming your {state.mode} appointment for {state.datetime}."
    st.session_state.messages.append({"role": "assistant", "content": confirmation_msg})
    
    try:
        EXCEL_PATH = "appointments.xlsx"
        columns = ["Date", "Day", "Time", "Mode", "Notes"]
        
        if os.path.exists(EXCEL_PATH):
            df = pd.read_excel(EXCEL_PATH)
            # Make sure all expected columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
        else:
            df = pd.DataFrame(columns=columns)
        
        # Parse date string to get components
        date_parts = state.datetime.split()
        
        if len(date_parts) >= 2:
            day = date_parts[0]  # e.g., "Sunday"
            time = ' '.join(date_parts[1:])  # e.g., "01:00 PM"
            
            # For date calculation
            import datetime as dt
            today = dt.datetime.now()
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            current_day_idx = today.weekday()  # 0 for Monday
            target_day_idx = days_of_week.index(day)
            
            days_ahead = (target_day_idx - current_day_idx) % 7
            if days_ahead == 0:  # Same day
                days_ahead = 7  # Next week
                
            target_date = today + dt.timedelta(days=days_ahead)
            formatted_date = target_date.strftime("%Y-%m-%d")  # e.g., "2025-06-15"
            
            # Check if the slot is already booked
            is_booked = any((df["Day"] == day) & (df["Time"] == time))

            if is_booked:
                conflict_msg = f"Sorry, {state.datetime} is already booked. Please choose another time. What other date and time would work for you?"
                st.session_state.messages.append({"role": "assistant", "content": conflict_msg})
                st.session_state.waiting_for_input = True
                st.session_state.input_context = "reschedule"
                return None
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
                
                # Save with error handling
                try:
                    # Sort by date and time for better calendar view
                    df["DateForSort"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors='coerce')
                    df = df.sort_values(by="DateForSort").drop(columns=["DateForSort"])
                    df.to_excel(EXCEL_PATH, index=False)
                    st.session_state.messages.append({"role": "assistant", "content": "Your appointment has been saved."})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"There was a problem saving your appointment. Please try again. Error: {str(e)}"})
                    return {"confirmed": False}
                
                return {"confirmed": True}
        else:
            st.session_state.messages.append({"role": "assistant", "content": "There was an issue with the date/time format."})
            return {"confirmed": False}
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Sorry, there was an issue with the booking system. Error: {str(e)}"})
        return {"confirmed": False}

# Function to process user input based on context
def process_contextual_input(user_input, context):
    current_state = st.session_state.current_state
    
    if context == "time_missing":
        # User is providing time after we asked for it
        combined_input = f"{current_state.user_input} at {user_input}"
        datetime_value = extract_datetime(combined_input)
        if datetime_value and datetime_value != "TIME_MISSING":
            st.session_state.messages.append({"role": "assistant", "content": f"Got it. Noted your preference for {datetime_value}."})
            current_state.datetime = datetime_value
            st.session_state.waiting_for_input = True
            st.session_state.input_context = "mode_selection"
            st.session_state.messages.append({"role": "assistant", "content": "Do you prefer a Virtual or Telephonic appointment?"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "I couldn't understand that time. Could you please try again with a format like '3 PM'?"})
    
    elif context == "mode_selection":
        # User is providing appointment mode
        mode_input = user_input.strip().lower()
        if "virtual" in mode_input:
            current_state.mode = "Virtual"
        elif "phone" in mode_input or "tele" in mode_input:
            current_state.mode = "Telephonic"
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I didn't catch that. Please specify 'Virtual' or 'Telephonic'."})
            return
        
        # Now handle confirmation
        result = handle_confirmation(current_state)
        if result is not None:
            current_state.confirmed = result.get("confirmed", False)
            st.session_state.waiting_for_input = False
            
    elif context == "reschedule":
        # User is providing a new time after conflict
        datetime_value = extract_datetime(user_input)
        if datetime_value and datetime_value != "TIME_MISSING":
            st.session_state.messages.append({"role": "assistant", "content": f"Got it. Updated your preference to {datetime_value}."})
            current_state.datetime = datetime_value
            result = handle_confirmation(current_state)
            if result is not None:
                current_state.confirmed = result.get("confirmed", False)
                st.session_state.waiting_for_input = False
        else:
            st.session_state.messages.append({"role": "assistant", "content": "I couldn't understand that time. Could you please try again with a format like 'Friday at 3 PM'?"})

# Handle regular input (non-contextual)
def process_regular_input(user_input):
    # Update the user input in the state
    current_state = st.session_state.current_state
    current_state.user_input = user_input
    
    # Override node implementations for Streamlit UI
    state_overrides = {}
    
    # For DateTimeExtractor node
    result = handle_datetime_extraction(current_state)
    if result is not None:
        for key, value in result.items():
            setattr(current_state, key, value)
            
        # If we successfully got a datetime, proceed to mode selection
        if current_state.datetime:
            handle_mode_selection(current_state)
    
# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Rerun to display the user message
    st.rerun()

# After displaying user message, process it
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_input = st.session_state.messages[-1]["content"]
    
    if st.session_state.waiting_for_input:
        # Handle contextual input (during a multi-step flow)
        process_contextual_input(user_input, st.session_state.input_context)
    else:
        # Handle regular input
        process_regular_input(user_input)
    
    # Rerun to display bot response
    st.rerun()

# Welcome message on first load
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.write("👋 Hi there! How can I help you today? I can assist with booking appointments or answer general questions.")
        st.session_state.messages.append({"role": "assistant", "content": "👋 Hi there! How can I help you today? I can assist with booking appointments or answer general questions."})
