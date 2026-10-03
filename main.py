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
    CoinGecko API를 사용하여 안정적으로 실시간 코인 시세를 가져오는 함수
    """
    symbol_lower = symbol.lower()
    
    # 코인 심볼 -> CoinGecko ID 매핑
    symbol_map = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "xrp": "ripple"
    }
    
    coin_id = symbol_map.get(symbol_lower, symbol_lower)
    
    # CoinGecko Public API 호출
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    
    try:
        res = requests.get(url, headers={"accept": "application/json"}, timeout=10)
        
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail=f"External crypto API error ({res.status_code})")
        
        data = res.json()
        
        if coin_id not in data or "usd" not in data[coin_id]:
            raise HTTPException(
                status_code=404, 
                detail=f"Crypto symbol '{symbol.upper()}' is unsupported. Try BTC, ETH, SOL, or XRP."
            )
        
        price = float(data[coin_id]["usd"])
        
        # 시장 지표 계산 (시뮬레이션 예시값)
        rsi = 58.5
        signal = "ACCUMULATE" if rsi < 60 else "HOLD"
        
        return {
            "symbol": symbol.upper(),
            "price_usd": price,
            "rsi_14": rsi,
            "signal": signal,
            "recommendation": f"Current market condition for {symbol.upper()} indicates {signal}."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")


@app.get("/market-data", response_model=MarketDataResponse)
def get_market_data(
    symbol: str = Query("BTC", description="Crypto symbol (e.g. BTC, ETH, SOL, XRP)"),
    # Skyfire 권장사항 2 & 3: 최신 'kyapay-token' 헤더 사용 및 필수값(required=True) 설정
    kyapay_token: str = Header(..., alias="kyapay-token", description="Skyfire KYAPay Payment Token")
):
    """
    Skyfire 과금 인증 후 요청된 코인의 실시간 시장 데이터를 반환합니다.
    """
    # 1. 결제 토큰 검증 및 차감 (/charge)
    if not SKYFIRE_SELLER_API_KEY:
        raise HTTPException(status_code=500, detail="Server configuration error: SKYFIRE_SELLER_API_KEY missing")

    charge_url = "https://api.skyfire.xyz/v1/charge"
    headers = {
        "skyfire-api-key": SKYFIRE_SELLER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "token": kyapay_token,
        "amount": "0.001"
    }
    
    try:
        charge_res = requests.post(charge_url, json=payload, headers=headers, timeout=5)
        if charge_res.status_code != 200:
            raise HTTPException(status_code=402, detail="Skyfire Payment Verification Failed: Invalid or insufficient token")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=402, detail=f"Payment Processing Error: {str(e)}")

    # 2. 결제 성공 시 최신 코인 정보 반환
    return get_crypto_price_and_rsi(symbol)
