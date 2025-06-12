# LangGraph State Machine Diagram

The following diagram illustrates the flow of the appointment booking assistant implemented with LangGraph:

    Start([Start]) --> IntentDetection
    
    IntentDetection{Intent Detection} -->|intent = "general"| GeneralQueryHandler
    IntentDetection -->|intent = "booking"| DateTimeExtractor
    IntentDetection -->|intent = unknown| FallbackNode
    
    GeneralQueryHandler[General Query Handler] --> IntentDetection
    
    DateTimeExtractor{DateTime Extractor} -->|datetime provided| ModeSelector
    DateTimeExtractor -->|datetime missing| FallbackNode
    
    FallbackNode[Fallback Node] --> DateTimeExtractor
    
    ModeSelector[Mode Selector] --> ConfirmationNode
    
    ConfirmationNode{Confirmation} -->|confirmed = true| End([End])
    ConfirmationNode -->|confirmed = false| DateTimeExtractor
    
    subgraph Legend
        A[Regular Node]
        B{Decision Node}
        C([Terminal Node])
    end

## State Transitions

1. **Entry Point**: The conversation begins at the Intent Detection node
2. **Intent Detection**: Determines if the user wants to book an appointment or ask a general question
3. **General Query Handler**: Processes and responds to general inquiries, then returns to Intent Detection
4. **DateTime Extractor**: Extracts date and time from user input:
   - If successful, proceeds to Mode Selection
   - If not, goes to Fallback Node for user to provide more information
5. **Mode Selection**: Determines whether the user wants a virtual or telephonic appointment
6. **Confirmation**: Validates and stores the appointment:
   - If successful, ends the conversation
   - If there's a conflict or error, returns to DateTime Extractor for rescheduling

## Key State Information

The state machine maintains and updates these key pieces of information:
- `user_input`: The current user message
- `intent`: "general" or "booking"
- `datetime`: The extracted appointment time
- `mode`: "Virtual" or "Telephonic"
- `confirmed`: Boolean indicating if appointment was successfully booked