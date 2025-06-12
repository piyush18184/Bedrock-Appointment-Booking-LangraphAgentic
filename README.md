# Appointment Booking Assistant

A conversational AI assistant that helps users book appointments through a structured conversation flow using LangGraph, AWS Bedrock, and dateparser.

## Features

- Natural language understanding of booking intents
- Date and time extraction from user messages
- Support for virtual and telephonic appointments
- Appointment conflict detection
- Persistent storage of appointments in Excel format
- Fallback mechanisms for handling unclear user inputs

## Architecture

The application uses a state machine architecture built with LangGraph:

1. **Intent Detection**: Identifies if the user wants to book an appointment or ask a general question
2. **DateTime Extraction**: Uses both dateparser and AWS Bedrock to understand complex time expressions
3. **Mode Selection**: Determines if the user wants a virtual or telephonic appointment
4. **Confirmation**: Validates, stores appointments, and handles scheduling conflicts

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure your AWS credentials for Bedrock access

## Usage

Run the assistant:

```
python main.py
```

Example conversation:
```
User: I'd like to book an appointment
Bot: Got it. Noted your preference for Monday 03:00 PM.
Bot: Do you prefer a Virtual or Telephonic appointment?
User: Virtual
Bot: Confirming your Virtual appointment for Monday 03:00 PM.
Bot: Your appointment has been saved.
```

## File Structure

- `main.py`: Entry point to run the assistant
- `graph/`
  - `state_machine.py`: LangGraph state machine definition
  - `nodes.py`: Node implementations for the state graph
- `services/`
  - `bedrock_llm.py`: AWS Bedrock LLM connector
  - `date_parser.py`: Date/time extraction service
- `requirements.txt`: Required Python packages

## Data Storage

Appointments are stored in `appointments.xlsx` with the following columns:
- Date: Calendar date (YYYY-MM-DD)
- Day: Day of the week
- Time: Appointment time
- Mode: Virtual or Telephonic
- Notes: Additional information from the user's request