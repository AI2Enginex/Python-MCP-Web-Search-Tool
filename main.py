from fastapi import FastAPI
from src.mcp_servers import chatbot

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "FastAPI is running"
    }

@app.post("/chat/{user_input}")
async def chat_endpoint(user_input: str):   
    """
    Endpoint to handle chat requests.

    Args:
        user_input: The input message from the user.

    Returns:
        The response from the chatbot.
    """
    response = await chatbot.chat_with_mcp(user_question=user_input)
    return {"response": response}