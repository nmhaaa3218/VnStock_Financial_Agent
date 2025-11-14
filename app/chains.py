"""
Chains for query classification, decomposition, and result combination.
"""
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models.chat_models import BaseChatModel


class QueryClassification(BaseModel):
    """Model for query classification result."""
    is_complex: bool = Field(description="True nếu câu hỏi phức tạp, False nếu đơn giản")
    reasoning: str = Field(description="Lý do phân loại")


class QueryDecomposition(BaseModel):
    """Model for query decomposition result."""
    sub_queries: list[str] = Field(description="Danh sách các câu hỏi con được phân tách từ câu hỏi phức tạp")
    reasoning: str = Field(description="Lý do phân tách câu hỏi")


class CombinedResult(BaseModel):
    """Model for combined result."""
    combined_answer: str = Field(description="Câu trả lời tổng hợp từ nhiều kết quả con")
    original_query: str = Field(description="Câu hỏi gốc")


def create_classifier_chain(llm: BaseChatModel):
    """Tạo chain để phân loại câu hỏi."""
    
    # Parser để chuyển đổi output thành Pydantic model
    parser = PydanticOutputParser(pydantic_object=QueryClassification)
    
    # Prompt template cho classifier
    classifier_prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là một chuyên gia phân loại câu hỏi tài chính.
        Nhiệm vụ: Phân loại câu hỏi thành True (phức tạp) hoặc False (đơn giản).
        
        Câu hỏi ĐƠN GIẢN (False): Chỉ cần 1 công cụ để trả lời (ví dụ: giá cổ phiếu, thông tin cơ bản)
        Câu hỏi PHỨC TẠP (True): Cần nhiều công cụ hoặc phân tích sâu (ví dụ: so sánh, xu hướng, dự đoán)
        
        {format_instructions}"""),
        ("human", "Phân loại câu hỏi sau: {query}")
    ])
    
    # Format instructions cho parser
    classifier_prompt = classifier_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Tạo chain
    classifier_chain = classifier_prompt | llm | parser
    
    return classifier_chain


def create_decomposition_chain(llm: BaseChatModel):
    """Tạo chain để phân tách câu hỏi phức tạp thành các câu hỏi con."""
    
    # Parser để chuyển đổi output thành Pydantic model
    parser = PydanticOutputParser(pydantic_object=QueryDecomposition)
    
    # Prompt template cho decomposition
    decomposition_prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là một chuyên gia phân tích câu hỏi tài chính.
        Nhiệm vụ: Phân tách câu hỏi phức tạp thành các câu hỏi con đơn giản hơn.
        
        Nguyên tắc phân tách:
        - Mỗi câu hỏi con chỉ cần 1 công cụ để trả lời
        - Các câu hỏi con phải có thứ tự logic
        - Đảm bảo câu hỏi con bao phủ toàn bộ câu hỏi gốc
        - Sử dụng mã cổ phiếu cụ thể nếu có
        
        Ví dụ:
        Câu hỏi: "So sánh hiệu suất VIC và VHM trong 3 tháng qua"
        Phân tách thành:
        1. "Xem dữ liệu OHLCV của VIC trong 3 tháng qua"
        2. "Xem dữ liệu OHLCV của VHM trong 3 tháng qua"
        3. "Tính RSI của VIC"
        4. "Tính RSI của VHM"
        
        {format_instructions}"""),
        ("human", "Phân tách câu hỏi sau: {query}")
    ])
    
    # Format instructions cho parser
    decomposition_prompt = decomposition_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Tạo chain
    decomposition_chain = decomposition_prompt | llm | parser
    
    return decomposition_chain


def create_combine_chain(llm: BaseChatModel):
    """Tạo chain để kết hợp nhiều kết quả thành một câu trả lời tổng hợp."""
    
    # Parser để chuyển đổi output thành Pydantic model
    parser = PydanticOutputParser(pydantic_object=CombinedResult)
    
    # Prompt template cho combining results
    combine_prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là một chuyên gia phân tích tài chính.
        Nhiệm vụ: Kết hợp nhiều kết quả từ các câu hỏi con thành một câu trả lời tổng hợp, mạch lạc.
        
        Nguyên tắc kết hợp:
        - Tổng hợp thông tin từ tất cả các kết quả
        - Tạo câu trả lời mạch lạc, dễ hiểu
        - So sánh và phân tích nếu có nhiều mã cổ phiếu
        - Đưa ra kết luận và khuyến nghị nếu phù hợp
        - Sử dụng tiếng Việt và định dạng dễ đọc
        
        {format_instructions}"""),
        ("human", """Câu hỏi gốc: {original_query}
        
        Các kết quả từ câu hỏi con:
        {results}
        
        Hãy kết hợp các kết quả trên thành một câu trả lời tổng hợp.""")
    ])
    
    # Format instructions cho parser
    combine_prompt = combine_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Tạo chain
    combine_chain = combine_prompt | llm | parser
    
    return combine_chain


def decompose_complex_query(query: str, llm: BaseChatModel) -> list[str]:
    """Phân tách câu hỏi phức tạp thành các câu hỏi con."""
    decomposition_chain = create_decomposition_chain(llm)
    result = decomposition_chain.invoke({"query": query})
    return result.sub_queries

