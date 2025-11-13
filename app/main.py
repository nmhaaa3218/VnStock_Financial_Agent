from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Import agent creation function from agent.py
from .agent import create_agent_executor

# --- Define Models for Request and Response ---

class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    input: str

class ChatResponse(BaseModel):
    """Response body for /chat endpoint."""
    output: str


# --- Initialize Application and Agent ---

app = FastAPI(
    title="VnStock LangChain Agent",
    description="An API for financial chatbot using LangChain and vnstock",
    version="1.0.0"
)

# Initialize agent_executor ONCE when server starts
agent_executor = create_agent_executor()

# --- Define API Endpoints ---

@app.get("/", tags=["Status"])
async def read_root():
    """Basic endpoint to check if server is running."""
    return {"status": "ok", "message": "Welcome to the VnStock Agent API!"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_agent(request: ChatRequest):
    """
    Main endpoint to chat with agent.
    Receives a question and returns an answer.
    """
    # Call agent (using ainvoke to run asynchronously)
    response = await agent_executor.ainvoke({
        "input": request.input
    })
    
    # Return the answer
    return ChatResponse(
        output=response['output']
    )