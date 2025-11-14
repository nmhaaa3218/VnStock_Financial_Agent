import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

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

def create_llm():
    """Create and return configured LLM."""
    return ChatGoogleGenerativeAI(
        model=Config.MODEL_NAME,
        temperature=Config.TEMPERATURE,
        top_k=Config.TOP_K,
        top_p=Config.TOP_P
    )

def get_system_prompt() -> str:
    """Get system prompt with today's date."""
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d")
    
    system_prompt = """Bạn là một trợ lý tài chính thông minh chuyên về thị trường chứng khoán Việt Nam.

    NHIỆM VỤ CHÍNH:
    - Trả lời các câu hỏi về cổ phiếu, công ty niêm yết trên sàn chứng khoán Việt Nam
    - Phân tích dữ liệu tài chính và đưa ra nhận định khách quan
    - Cung cấp thông tin chính xác dựa trên dữ liệu từ vnstock

    NGUYÊN TẮC LÀM VIỆC:
    1. Luôn sử dụng các công cụ có sẵn để truy xuất dữ liệu thực tế
    2. Trả lời bằng tiếng Việt, ngôn ngữ rõ ràng, dễ hiểu
    3. Định dạng kết quả dưới dạng bảng hoặc danh sách khi phù hợp
    4. Nếu không tìm thấy thông tin, hãy nói rõ và đề xuất cách khác
    5. Đưa ra phân tích khách quan, không khuyến nghị mua/bán cụ thể

    CÁCH XỬ LÝ CÂU HỎI:
    - Xác định mã cổ phiếu từ câu hỏi (VD: VIC, VCB, FPT...)
    - Chọn công cụ phù hợp để lấy dữ liệu
    - Phân tích và trình bày kết quả một cách có hệ thống
    - Giải thích các chỉ số kỹ thuật nếu được hỏi

    LƯU Ý:
    - Hôm nay là ngày {today}
    - Dữ liệu có thể có độ trễ, hãy thông báo nếu cần thiết
    - Luôn kiểm tra tính hợp lệ của mã cổ phiếu trước khi truy xuất dữ liệu"""
    
    return system_prompt.format(today=today)

def create_agent_executor():
    """This function creates and returns a configured agent for simple queries.
    Follows the notebook implementation exactly."""
    
    # 1. Initialize LLM
    llm = create_llm()

    # 2. List of tools (regular tools without return_direct)
    all_tools = [
        ViewOHLCVTool(),
        ViewManagementTool(),
        ViewShareholdersTool(),
        ViewSubsidiariesTool(),
        CalculateTotalVolumeTool(),
        CalculateSMATool(),
        CalculateRSITool()
    ]

    # 3. Get system prompt (matching notebook format)
    system_prompt = get_system_prompt()

    # 4. Create Agent using create_agent (matching notebook exactly)
    agent = create_agent(
        model=llm,
        tools=all_tools,
        system_prompt=system_prompt,
        debug=False
    )
    
    return agent


def create_direct_agent_executor():
    """This function creates and returns a configured agent with return_direct=True for complex queries.
    Follows the notebook implementation exactly."""
    
    # 1. Initialize LLM
    llm = create_llm()

    # 2. List of tools with return_direct=True (matching notebook)
    # Note: BaseTool doesn't accept return_direct in constructor, so we set it after creation
    direct_tools = [
        ViewOHLCVTool(return_direct=True),
        ViewManagementTool(return_direct=True),
        ViewShareholdersTool(return_direct=True),
        ViewSubsidiariesTool(return_direct=True),
        CalculateTotalVolumeTool(return_direct=True),
        CalculateSMATool(return_direct=True),
        CalculateRSITool(return_direct=True)
    ]

    # 3. Get system prompt (matching notebook format)
    system_prompt = get_system_prompt()

    # 4. Create Agent using create_agent (matching notebook exactly)
    agent = create_agent(
        model=llm,
        tools=direct_tools,
        system_prompt=system_prompt,
        debug=False
    )
    
    return agent