from fastapi import FastAPI, Header, HTTPException, Depends
import requests
import os

app = FastAPI(
    title="Skyfire Powered AI Agent API",
    description="Skyfire AI Agent Economy - USDC Micro-payment API for Autonomous Agents",
    version="3.1.0"
)

# ------------------------------------------------------------------
# [환경 변수 설정]
# Render 대시보드의 Environment Variables에 SKYFIRE_SELLER_API_KEY를 추가하거나,
# 아래 따옴표 안에 발급받은 Skyfire Seller API Key를 직접 넣으세요.
# ------------------------------------------------------------------
SKYFIRE_SELLER_API_KEY = os.getenv("7c022faf-b3de-4db6-9cfb-e66e49ca9ada")

def verify_and_charge_skyfire_token(
    skyfire_pay_id: str = Header(None, alias="skyfire-pay-id"),
    x_agent_token: str = Header(None, alias="X-Agent-Token")
):
    """
    외부 AI 에이전트가 보낸 Skyfire 결제 토큰(skyfire-pay-id 또는 X-Agent-Token)을 검증하고 
    Skyfire 게이트웨이로 즉시 정산(Charge)을 진행합니다.
    """
    # 두 헤더 중 하나라도 존재하면 토큰으로 사용
    token = skyfire_pay_id or x_agent_token
    
    if not token:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Payment Required",
                "payment_network": "Skyfire Trust Stack",
                "price_usd": 0.001,
                "message": "Please include Skyfire JWT in 'skyfire-pay-id' or 'X-Agent-Token' header."
            }
        )
    
    # Skyfire 서버로 토큰 차감(Charge) 요청 전송
    try:
        charge_response = requests.post(
            "https://api.skyfire.xyz/api/v1/tokens/charge",
            headers={
                "Authorization": f"Bearer {SKYFIRE_SELLER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "token": token,
                "amount": "0.001"
            },
            timeout=5
        )
        
        # 차감 실패 시 402 반환
        if charge_response.status_code != 200:
            raise HTTPException(
                status_code=402, 
                detail=f"Skyfire Payment Verification Failed: {charge_response.text}"
            )
            
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Skyfire Gateway Communication Error: {str(e)}"
        )
        
    return True

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "AI Agent Market Intelligence (Skyfire Integrated)",
        "price_per_call": "$0.001 USDC",
        "docs_for_agents": "/openapi.json"
    }

@app.get("/api/v1/market-data", dependencies=[Depends(verify_and_charge_skyfire_token)])
def get_market_data(symbol: str = "BTC"):
    """
    [유료 API] Skyfire 결제 차감이 성공한 AI 에이전트에게 전달되는 정밀 데이터
    """
    return {
        "status": "success",
        "symbol": symbol.upper(),
        "market_price": 95200.0,
        "rsi_14": 62.4,
        "sentiment": "Bullish",
        "agent_action": "ACCUMULATE",
        "payment_status": "Skyfire Token Charged Successfully"
    }
