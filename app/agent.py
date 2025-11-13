import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import Config
from .tools import (
    ViewOHLCVTool,
    ViewManagementTool,
    ViewShareholdersTool,
    ViewSubsidiariesTool,
    CalculateTotalVolumeTool,
    CalculateSMATool,
    CalculateRSITool
)

def create_agent_executor():
    """This function creates and returns a configured agent executor."""
    
    # 1. Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=Config.MODEL_NAME,
        temperature=Config.TEMPERATURE,
        top_k=Config.TOP_K,
        top_p=Config.TOP_P,
        convert_system_message_to_human=True # Important for Gemini
    )

    # 2. List of tools
    all_tools = [
        ViewOHLCVTool(),
        ViewManagementTool(),
        ViewShareholdersTool(),
        ViewSubsidiariesTool(),
        CalculateTotalVolumeTool(),
        CalculateSMATool(),
        CalculateRSITool()
    ]

    # 3. Create Prompt
    # Get today's date (Vietnam timezone)
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d")

    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""Bạn là một trợ lý tài chính thông minh chuyên về thị trường chứng khoán Việt Nam.
        Bạn có thể truy cập dữ liệu từ vnstocks.com để cung cấp thông tin chính xác.
        Sử dụng các công cụ có sẵn để truy xuất dữ liệu.
        Luôn hiển thị kết quả bằng tiếng Việt và định dạng dễ đọc.
        Nếu không thể tìm thấy thông tin, hãy nói rõ. 
        Hôm nay là ngày {today}."""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. Create Agent
    agent = create_tool_calling_agent(llm, all_tools, agent_prompt)

    # 5. Create Agent Executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True 
    )
    
    return agent_executor