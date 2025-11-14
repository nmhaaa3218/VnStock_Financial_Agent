from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Import agent creation functions and chains
from .agent import create_agent_executor, create_direct_agent_executor, create_llm
from .chains import create_classifier_chain, create_decomposition_chain, create_combine_chain

# --- Define Models for Request and Response ---

class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    input: str

class ChatResponse(BaseModel):
    """Response body for /chat endpoint."""
    output: str


# --- Initialize Application and Agents ---

app = FastAPI(
    title="VnStock LangChain Agent",
    description="An API for financial chatbot using LangChain and vnstock",
    version="1.0.0"
)

# Initialize agents and chains ONCE when server starts
llm = create_llm()
agent = create_agent_executor()
agent_direct = create_direct_agent_executor()
classifier_chain = create_classifier_chain(llm)
decomposition_chain = create_decomposition_chain(llm)
combine_chain = create_combine_chain(llm)

# --- Define API Endpoints ---

@app.get("/", tags=["Status"])
async def read_root():
    """Basic endpoint to check if server is running."""
    return {"status": "ok", "message": "Welcome to the VnStock Agent API!"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_agent(request: ChatRequest):
    """
    Main endpoint to chat with agent.
    Implements the workflow from experiment.ipynb exactly:
    1. Classify query as simple or complex
    2. If simple: use regular agent (no history maintained)
    3. If complex: decompose -> use direct agents -> combine results
    
    Each query is independent - no chat history is maintained.
    """
    query = request.input
    
    # Step 1: Classify the query (matching notebook: classifier_chain.invoke)
    classification_result = await classifier_chain.ainvoke({"query": query})
    
    if classification_result.is_complex:
        # Complex query workflow: decompose -> execute sub-queries -> combine
        # Step 2: Decompose complex query into sub-queries (matching notebook)
        decomposition_result = await decomposition_chain.ainvoke({"query": query})
        decomposed_queries = decomposition_result.sub_queries
        
        # Step 3: Execute each sub-query using direct agent (matching notebook exactly)
        # Each invocation is independent - no history passed
        results = []
        for sub_query in decomposed_queries:
            agent_result = await agent_direct.ainvoke({
                "messages": [{"role": "user", "content": sub_query}]
            })
            results.append(agent_result)
        
        # Step 4: Format results for combination (matching notebook exactly)
        formatted_results = ""
        for i, result in enumerate(results, 1):
            # Extract output matching notebook: result.get('output', str(result))
            # Add error handling for different response structures
            try:
                if isinstance(result, dict):
                    output = result.get('output', str(result))
                else:
                    output = str(result)
            except Exception as e:
                output = f"Error extracting result {i}: {str(e)}"
            
            # Ensure output is a string
            if not isinstance(output, str):
                output = str(output)
            
            formatted_results += f"Kết quả {i}:\n{output}\n\n"
        
        # Step 5: Combine results using combine chain (matching notebook)
        combined_result = await combine_chain.ainvoke({
            "original_query": query,
            "results": formatted_results
        })
        
        # Return combined answer
        # Ensure combined_answer is a string
        combined_output = combined_result.combined_answer
        if not isinstance(combined_output, str):
            combined_output = str(combined_output)
        
        return ChatResponse(
            output=combined_output
        )
    else:
        # Simple query: use regular agent (matching notebook exactly)
        # Each query is independent - no history passed or maintained
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": query}]
        })
        
        # Extract output matching notebook: result['messages'][-1].content
        # The content can be a list with dict containing 'text' field (for AIMessage)
        # Add error handling for different response structures
        try:
            if 'messages' in result and len(result['messages']) > 0:
                last_message = result['messages'][-1]
                
                # Get content from message object or dict
                if hasattr(last_message, 'content'):
                    content = last_message.content
                elif isinstance(last_message, dict) and 'content' in last_message:
                    content = last_message['content']
                else:
                    content = str(last_message)
                
                # Handle content that is a list (AIMessage format)
                if isinstance(content, list) and len(content) > 0:
                    # Check if it's a dict with 'text' field
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        output = content[0]['text']
                    else:
                        output = str(content[0])
                elif isinstance(content, str):
                    output = content
                else:
                    output = str(content)
            elif 'output' in result:
                output = result['output']
            else:
                output = str(result)
        except (KeyError, IndexError, AttributeError) as e:
            # Fallback if structure is unexpected
            output = f"Error extracting response: {str(e)}. Result structure: {type(result)}"
        
        # Ensure output is a string
        if not isinstance(output, str):
            output = str(output)
        
        return ChatResponse(
            output=output
        )