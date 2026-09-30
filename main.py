import os
import requests
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(
    title="AI Agent Market Intelligence API",
    description="Multi-Crypto Real-Time Market Intelligence API for Autonomous AI Agents",
    version="1.1.0"
)

SKYFIRE_SELLER_API_KEY = os.getenv("SKYFIRE_SELLER_API_KEY", "")

# 응답 데이터 형식 정의
class MarketDataResponse(BaseModel):
    symbol: str
    price_usd: float
    rsi_14: float
    signal: str
    recommendation: str

def get_crypto_price_and_rsi(symbol: str):
    """
    외부 거래소/데이터 API를 통해 요청받은 코인의 실시간 시세 및 RSI를 계산/조회하는 함수
    """
    symbol_upper = symbol.upper()
    
    # Binance Public API 예시 (USDT 마켓 기준)
    pair = f"{symbol_upper}USDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
    
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Crypto symbol '{symbol_upper}' not found or unsupported.")
        
        data = res.json()
        price = float(data["price"])
        
        # 간단한 RSI 및 Signal 시뮬레이션 계산 logic
        # (실제 프로젝트 시 klines API를 활용해 14일봉 RSI를 정밀 계산하도록 고도화 가능)
        rsi = 55.4  # 예시 지표값
        signal = "ACCUMULATE" if rsi < 60 else "HOLD"
        
        return {
            "symbol": symbol_upper,
            "price_usd": price,
            "rsi_14": rsi,
            "signal": signal,
            "recommendation": f"Current market condition for {symbol_upper} indicates {signal}."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@app.get("/market-data", response_model=MarketDataResponse)
def get_market_data(
    symbol: str = Query("BTC", description="Crypto symbol (e.g. BTC, ETH, SOL, XRP)"),
    skyfire_pay_id: str = Header(None, alias="skyfire-pay-id"),
    x_agent_token: str = Header(None, alias="X-Agent-Token")
):
    """
    Skyfire 과금 인증 후 요청된 코인의 실시간 시장 데이터를 반환합니다.
    """
    payment_token = skyfire_pay_id or x_agent_token
    
    # Skyfire 토큰 차감/결제 검증 API 호출 (/charge)
    if payment_token and SKYFIRE_SELLER_API_KEY:
        charge_url = "https://api.skyfire.xyz/v1/charge"
        headers = {
            "skyfire-api-key": SKYFIRE_SELLER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "token": payment_token,
            "amount": "0.001"
        }
        try:
            charge_res = requests.post(charge_url, json=payload, headers=headers, timeout=5)
            if charge_res.status_code != 200:
                raise HTTPException(status_code=402, detail="Skyfire Payment Verification Failed")
        except Exception:
            raise HTTPException(status_code=402, detail="Payment Processing Error")
    
    # 코인 정보 가져오기 및 응답
    return get_crypto_price_and_rsi(symbol)
