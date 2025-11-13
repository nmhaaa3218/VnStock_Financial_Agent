import os
import pandas as pd
from typing import Type, Optional, List
from pydantic import BaseModel, Field
from vnstock import Company
from vnstock import Quote
import pandas_ta_classic as ta
from langchain.tools import BaseTool

#============Shareholders============
class ViewShareholdersInput(BaseModel):
    """Input for viewing shareholders of a Vietnamese company."""
    symbol: str = Field(description="Stock symbol of the Vietnamese company (e.g., 'VIC', 'VCB')")


class ViewShareholdersTool(BaseTool):
    """Tool to view shareholders information of Vietnamese companies using vnstock."""
    
    name: str = "view_shareholders"
    description: str = "Get shareholders information for a Vietnamese stock symbol. Use this when you need to find information about major shareholders, ownership structure of a Vietnamese company."
    args_schema: Type[BaseModel] = ViewShareholdersInput
    
    def _run(self, symbol: str) -> str:
        """Execute the tool to get shareholders information."""
        try:
            company = Company(symbol=symbol, source='TCBS')
            shareholders_data = company.shareholders()
            
            if shareholders_data is None or shareholders_data.empty:
                return f"Không tìm thấy thông tin cổ đông cho mã {symbol}"
            
            return shareholders_data.to_json(orient='records', force_ascii=False)
            
        except Exception as e:
            return f"Lỗi khi lấy thông tin cổ đông cho mã {symbol}: {str(e)}"
    
    async def _arun(self, symbol: str) -> str:
        """Async version of the tool."""
        return self._run(symbol)

# Create an instance of the tool and invoke it
# result = ViewShareholdersTool().invoke({'symbol': 'VCB'})
# print(result)

#============Management============
class ViewManagementInput(BaseModel):
    """Input for viewing management of a Vietnamese company."""
    symbol: str = Field(description="Stock symbol of the Vietnamese company (e.g., 'VIC', 'VCB')")


class ViewManagementTool(BaseTool):
    """Tool to view management information of Vietnamese companies using vnstock."""
    
    name: str = "view_management"
    description: str = "Get management information for a Vietnamese stock symbol. Use this when you need to find information about company officers, management team, executives of a Vietnamese company."
    args_schema: Type[BaseModel] = ViewManagementInput
    
    def _run(self, symbol: str) -> str:
        """Execute the tool to get management information."""
        try:
            company = Company(symbol=symbol, source='TCBS')
            management_data = company.officers(filter_by='working')
            
            if management_data is None or management_data.empty:
                return f"Không tìm thấy thông tin ban lãnh đạo cho mã {symbol}"
            
            return management_data.to_json(orient='records', force_ascii=False)
            
        except Exception as e:
            return f"Lỗi khi lấy thông tin ban lãnh đạo cho mã {symbol}: {str(e)}"
    
    async def _arun(self, symbol: str) -> str:
        """Async version of the tool."""
        return self._run(symbol)

# Create an instance of the tool and invoke it
# result = ViewManagementTool().invoke({'symbol': 'TCB'})
# print(result)

# ============Subsidaries============
class ViewSubsidiariesInput(BaseModel):
    """Input for viewing subsidiaries of a Vietnamese company."""
    symbol: str = Field(description="Stock symbol of the Vietnamese company (e.g., 'VIC', 'VCB')")


class ViewSubsidiariesTool(BaseTool):
    """Tool to view subsidiaries information of Vietnamese companies using vnstock."""
    
    name: str = "view_subsidiaries"
    description: str = "Get subsidiaries information for a Vietnamese stock symbol. Use this when you need to find information about subsidiary companies, affiliated companies of a Vietnamese company."
    args_schema: Type[BaseModel] = ViewSubsidiariesInput
    
    def _run(self, symbol: str) -> str:
        """Execute the tool to get subsidiaries information."""
        try:
            company = Company(symbol=symbol, source='TCBS')
            subsidiaries_data = company.subsidiaries()
            
            if subsidiaries_data is None or subsidiaries_data.empty:
                return f"Không tìm thấy thông tin công ty con cho mã {symbol}"
            
            return subsidiaries_data.to_json(orient='records', force_ascii=False)
            
        except Exception as e:
            return f"Lỗi khi lấy thông tin công ty con cho mã {symbol}: {str(e)}"
    
    async def _arun(self, symbol: str) -> str:
        """Async version of the tool."""
        return self._run(symbol)

# Create an instance of the tool and invoke it
# result = ViewSubsidiariesTool().invoke({'symbol': 'TCB'})
# print(result)

# ============OHLCV============
class ViewOHLCVInput(BaseModel):
    """Input for viewing OHLCV data of a Vietnamese company."""
    symbol: str = Field(description="Stock symbol of the Vietnamese company (e.g., 'VIC', 'VCB')")
    start: str = Field(description="Start date for OHLCV data in YYYY-mm-dd format", default="2024-01-01")
    end: str = Field(description="End date for OHLCV data in YYYY-mm-dd format", default="2024-12-31")
    interval: str = Field(description="Timeframe for OHLCV data. Available options: '1m' (1 minute), '5m' (5 minutes), '15m' (15 minutes), '30m' (30 minutes), '1H' (1 hour), '1D' (1 day), '1W' (1 week), '1M' (1 month)", default="1D")
    columns: Optional[List[str]] = Field(description="List of columns to return. Available options: ['time', 'open', 'high', 'low', 'close', 'volume']. If not specified, all columns will be returned.", default=None)


class ViewOHLCVTool(BaseTool):
    """Tool to view OHLCV (Open, High, Low, Close, Volume) data of Vietnamese companies using vnstock."""
    
    name: str = "view_ohlcv"
    description: str = "Get OHLCV (Open, High, Low, Close, Volume) data for a Vietnamese stock symbol with specified timeframe and date range. You can select specific columns like 'open', 'close', 'volume', etc. Use this when you need historical price data, trading volume, or technical analysis data."
    args_schema: Type[BaseModel] = ViewOHLCVInput
    
    def _run(self, symbol: str, start: str = "2024-01-01", end: str = "2024-12-31", interval: str = "1D", columns: Optional[list] = None) -> str:
        """Execute the tool to get OHLCV data."""
        try:
            # Validate interval
            valid_intervals = ['1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M']
            if interval not in valid_intervals:
                return f"Khung thời gian không hợp lệ. Các khung thời gian có sẵn: {', '.join(valid_intervals)}"
            
            # Validate columns if provided
            available_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            if columns:
                invalid_columns = [col for col in columns if col not in available_columns]
                if invalid_columns:
                    return f"Cột không hợp lệ: {', '.join(invalid_columns)}. Các cột có sẵn: {', '.join(available_columns)}"
            
            quote = Quote(symbol=symbol, source='TCBS')
            ohlcv_data = quote.history(start=start, end=end, interval=interval)
            
            if ohlcv_data is None or ohlcv_data.empty:
                return f"Không tìm thấy dữ liệu OHLCV cho mã {symbol} từ {start} đến {end} với khung thời gian {interval}"
            
            # Filter columns if specified
            if columns:
                # Ensure 'time' is always included if other columns are selected
                if 'time' not in columns and len(columns) > 0:
                    columns = ['time'] + columns
                
                # Filter the dataframe to only include requested columns
                available_cols_in_data = [col for col in columns if col in ohlcv_data.columns]
                if available_cols_in_data:
                    ohlcv_data = ohlcv_data[available_cols_in_data]
                else:
                    return f"Không tìm thấy cột nào trong dữ liệu cho mã {symbol}"
            
            return ohlcv_data.to_json(orient='records', force_ascii=False)
            
        except Exception as e:
            return f"Lỗi khi lấy dữ liệu OHLCV cho mã {symbol}: {str(e)}"
    
    async def _arun(self, symbol: str, start: str = "2025-10-01", end: str = "2025-11-13", interval: str = "1D", columns: Optional[list] = None) -> str:
        """Async version of the tool."""
        return self._run(symbol, start, end, interval, columns)


# result = ViewOHLCVTool().invoke({"symbol": "VCB", "start": "2025-10-01", "end": "2025-11-13", "interval": "15m", "columns": ["open", "close", "volume"]})
# print(result)

#============Volume Profile============
class CalculateTotalVolumeInput(BaseModel):
    """Input schema for Calculate Total Volume tool."""
    symbol: str = Field(description="Mã cổ phiếu (ví dụ: VCB, VIC, FPT)")
    start: str = Field(default="2024-01-01", description="Ngày bắt đầu (YYYY-MM-DD)")
    end: str = Field(default="2024-12-31", description="Ngày kết thúc (YYYY-MM-DD)")
    interval: str = Field(default="1D", description="Khung thời gian (1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M)")

class CalculateTotalVolumeTool(BaseTool):
    """Tool to calculate total volume for Vietnamese stocks in a specified timeframe."""
    
    name: str = "calculate_total_volume"
    description: str = "Tính tổng khối lượng giao dịch của cổ phiếu Việt Nam trong khoảng thời gian chỉ định. Trả về tổng khối lượng."
    args_schema: Type[BaseModel] = CalculateTotalVolumeInput
    
    def _run(self, symbol: str, start: str = "2024-01-01", end: str = "2024-12-31", interval: str = "1D") -> str:
        """Execute the tool to calculate total volume."""
        try:
            # Validate interval
            valid_intervals = ['1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M']
            if interval not in valid_intervals:
                return f"Khung thời gian không hợp lệ. Các khung thời gian có sẵn: {', '.join(valid_intervals)}"
            
            quote = Quote(symbol=symbol, source='TCBS')
            ohlcv_data = quote.history(start=start, end=end, interval=interval)
            
            if ohlcv_data is None or ohlcv_data.empty:
                return f"Không tìm thấy dữ liệu OHLCV cho mã {symbol} từ {start} đến {end} với khung thời gian {interval}"
            
            # Check if volume column exists
            if 'volume' not in ohlcv_data.columns:
                return f"Không tìm thấy cột 'volume' trong dữ liệu cho mã {symbol}"
            
            # Calculate total volume
            total_volume = ohlcv_data['volume'].sum()
            
            return str(int(total_volume))
            
        except Exception as e:
            return f"Lỗi khi tính tổng khối lượng cho mã {symbol}: {str(e)}"
    
    async def _arun(self, symbol: str, start: str = "2024-01-01", end: str = "2024-12-31", interval: str = "1D") -> str:
        """Async version of the tool."""
        return self._run(symbol, start, end, interval)

# result = CalculateTotalVolumeTool().invoke({"symbol": "VCB", "start": "2024-10-01", "end": "2024-11-13", "interval": "1D"})
# print(result)


#============Technical Indicators============
class CalculateSMAInput(BaseModel):
    """Input schema for Calculate SMA tool."""
    symbol: str = Field(description="Mã cổ phiếu (ví dụ: VCB, VIC, FPT)")
    start: str = Field(default="2024-01-01", description="Ngày bắt đầu (YYYY-MM-DD)")
    end: str = Field(default="2024-12-31", description="Ngày kết thúc (YYYY-MM-DD)")
    interval: str = Field(default="1D", description="Khung thời gian (1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M)")
    period: int = Field(default=20, description="Chu kỳ tính SMA (ví dụ: 20 cho SMA 20 ngày)")

class CalculateSMATool(BaseTool):
    """Tool to calculate Simple Moving Average (SMA) for Vietnamese stocks."""
    
    name: str = "calculate_sma"
    description: str = "Tính toán đường trung bình động đơn giản (SMA) cho cổ phiếu Việt Nam. Trả về dữ liệu OHLCV kèm theo cột SMA."
    args_schema: Type[BaseModel] = CalculateSMAInput
    
    def _run(self, symbol: str, start: str = "2024-01-01", end: str = "2024-12-31", interval: str = "1D", period: int = 20) -> str:
        """Execute the tool to calculate SMA."""
        try:
            # Validate interval
            valid_intervals = ['1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M']
            if interval not in valid_intervals:
                return f"Khung thời gian không hợp lệ. Các khung thời gian có sẵn: {', '.join(valid_intervals)}"
            
            # Validate period
            if period <= 0:
                return f"Chu kỳ SMA phải là số dương. Giá trị nhận được: {period}"
            
            quote = Quote(symbol=symbol, source='TCBS')
            ohlcv_data = quote.history(start=start, end=end, interval=interval)
            
            if ohlcv_data is None or ohlcv_data.empty:
                return f"Không tìm thấy dữ liệu OHLCV cho mã {symbol} từ {start} đến {end} với khung thời gian {interval}"
            
            # Calculate SMA using pandas_ta
            if 'close' not in ohlcv_data.columns:
                return f"Không tìm thấy cột 'close' trong dữ liệu cho mã {symbol}"
            
            # Calculate Simple Moving Average using pandas_ta
            ohlcv_data[f'SMA_{period}'] = ta.sma(ohlcv_data['close'], length=period)
            
            # Round SMA values to 2 decimal places for better readability
            ohlcv_data[f'SMA_{period}'] = ohlcv_data[f'SMA_{period}'].round(2)
            
            return ohlcv_data.to_json(orient='records', force_ascii=False)
            
        except Exception as e:
            return f"Lỗi khi tính toán SMA cho mã {symbol}: {str(e)}"
    
    async def _arun(self, symbol: str, start: str = "2024-01-01", end: str = "2024-12-31", interval: str = "1D", period: int = 20) -> str:
        """Async version of the tool."""
        return self._run(symbol, start, end, interval, period)

# result = CalculateSMATool().invoke({"symbol": "VCB", "start": "2024-10-01", "end": "2024-11-13", "interval": "1D", "period": 20})
# print(result)

#============RSI============
class CalculateRSIInput(BaseModel):
    """Input schema for Calculate RSI tool."""
    symbol: str = Field(description="Mã cổ phiếu (ví dụ: VCB, VIC, FPT)")
    start: str = Field(default="2024-01-01", description="Ngày bắt đầu (YYYY-MM-DD)")
    end: str = Field(default="2024-12-31", description="Ngày kết thúc (YYYY-MM-DD)")
    interval: str = Field(default="1D", description="Khung thời gian (1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M)")
    period: int = Field(default=14, description="Chu kỳ tính RSI (ví dụ: 14 cho RSI 14 ngày)")

class CalculateRSITool(BaseTool):
    """Tool to calculate Relative Strength Index (RSI) for Vietnamese stocks."""
    
    name: str = "calculate_rsi"
    description: str = "Tính toán chỉ số sức mạnh tương đối (RSI) cho cổ phiếu Việt Nam. Trả về dữ liệu OHLCV kèm theo cột RSI."
    args_schema: Type[BaseModel] = CalculateRSIInput
    
    def _run(self, symbol: str, start: str = "2024-01-01", end: str = "2024-12-31", interval: str = "1D", period: int = 14) -> str:
        """Execute the tool to calculate RSI."""
        try:
            # Validate interval
            valid_intervals = ['1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M']
            if interval not in valid_intervals:
                return f"Khung thời gian không hợp lệ. Các khung thời gian có sẵn: {', '.join(valid_intervals)}"
            
            # Validate period
            if period <= 0:
                return f"Chu kỳ RSI phải là số dương. Giá trị nhận được: {period}"
            
            quote = Quote(symbol=symbol, source='TCBS')
            ohlcv_data = quote.history(start=start, end=end, interval=interval)
            
            if ohlcv_data is None or ohlcv_data.empty:
                return f"Không tìm thấy dữ liệu OHLCV cho mã {symbol} từ {start} đến {end} với khung thời gian {interval}"
            
            # Calculate RSI using pandas_ta
            if 'close' not in ohlcv_data.columns:
                return f"Không tìm thấy cột 'close' trong dữ liệu cho mã {symbol}"
            
            # Calculate RSI using pandas_ta
            ohlcv_data[f'RSI_{period}'] = ta.rsi(ohlcv_data['close'], length=period)
            
            # Round RSI values to 2 decimal places for better readability
            ohlcv_data[f'RSI_{period}'] = ohlcv_data[f'RSI_{period}'].round(2)
            
            return ohlcv_data.to_json(orient='records', force_ascii=False)
            
        except Exception as e:
            return f"Lỗi khi tính toán RSI cho mã {symbol}: {str(e)}"
    
    async def _arun(self, symbol: str, start: str = "2024-01-01", end: str = "2024-12-31", interval: str = "1D", period: int = 14) -> str:
        """Async version of the tool."""
        return self._run(symbol, start, end, interval, period)

# result = CalculateRSITool().invoke({"symbol": "VCB", "start": "2024-10-01", "end": "2024-11-13", "interval": "1D", "period": 28})
# print(result)

#============Tool Calling ============
all_tools = [
    ViewOHLCVTool(),
    ViewManagementTool(),
    ViewShareholdersTool(),
    ViewSubsidiariesTool(),
    CalculateTotalVolumeTool(),
    CalculateSMATool(),
    CalculateRSITool()
]
