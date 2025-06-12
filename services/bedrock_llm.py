# services/bedrock_llm.py

from langchain_aws import ChatBedrock

llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",  # or your latest model ID
    model_kwargs={
        "temperature": 0.7,
        "max_tokens": 100
    },
    region_name="us-east-1"
)

def call_llm(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content.strip()
