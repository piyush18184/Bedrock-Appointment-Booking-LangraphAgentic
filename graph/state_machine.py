from langgraph.graph import StateGraph
from graph.nodes import (
    detect_intent_node,
    general_query_node,
    extract_datetime_node,
    mode_selection_node,
    confirmation_node,
    fallback_node
)
from pydantic import BaseModel
from typing import Optional, List


class AssistantState(BaseModel):
    user_input: str
    intent: Optional[str] = ""
    datetime: Optional[str] = ""
    mode: Optional[str] = ""
    history: Optional[List[str]] = []
    confirmed: Optional[bool] = None  # ✅ ADD THIS LINE


def build_langgraph():
    builder = StateGraph(AssistantState)

    builder.add_node("IntentDetection", detect_intent_node)
    builder.add_node("GeneralQueryHandler", general_query_node)
    builder.add_node("DateTimeExtractor", extract_datetime_node)
    builder.add_node("ModeSelector", mode_selection_node)
    builder.add_node("ConfirmationNode", confirmation_node)
    builder.add_node("FallbackNode", fallback_node)

    builder.set_entry_point("IntentDetection")

    builder.add_edge("GeneralQueryHandler", "IntentDetection")
    def route_from_intent(state):
        if state.intent == "general":
            return "GeneralQueryHandler"
        elif state.intent == "booking":
            return "DateTimeExtractor"
        else:
            return "FallbackNode"  # optional fallback
    builder.add_conditional_edges("IntentDetection", route_from_intent)
    def route_after_datetime(state):
        return "ModeSelector" if state.datetime else "FallbackNode"
    builder.add_conditional_edges("DateTimeExtractor", route_after_datetime)
    builder.add_edge("FallbackNode", "DateTimeExtractor")
    builder.add_edge("ModeSelector", "ConfirmationNode")
    def route_after_confirmation(state):
        return "End" if state.confirmed else "DateTimeExtractor"
    builder.add_conditional_edges("ConfirmationNode", route_after_confirmation)
    builder.add_node("End", lambda state: state)

    return builder.compile()
