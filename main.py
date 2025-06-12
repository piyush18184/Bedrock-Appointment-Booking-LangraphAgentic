from graph.state_machine import build_langgraph

def run_assistant():
    graph = build_langgraph()
    graph.invoke({"user_input": "Hi!", "intent": "", "datetime": "", "mode": "", "history": []})

if __name__ == "__main__":
    run_assistant()