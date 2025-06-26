# services/bedrock_llm.py

from langchain_aws import ChatBedrock

llm = ChatBedrock(
    model_id="",  # or your latest model ID
    model_kwargs={
        "temperature": 0.7,
        "max_tokens": 100
    },
    region_name=""
)

def call_llm(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content.strip()
