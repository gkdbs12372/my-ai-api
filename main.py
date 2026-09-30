from fastapi import FastAPI, Header, HTTPException, Depends
import requests
import os

app = FastAPI(title="Agent Revenue API")

# 환경 변수로 API 키 관리 (지갑/판매자 키)
MY_SELLER_API_KEY = os.getenv("MY_SELLER_API_KEY", "default_test_key")

def verify_agent_payment(x_agent_token: str = Header(..., alias="X-Agent-Token")):
    """
    AI 에이전트가 헤더로 보낸 토큰을 검증하는 로직
    """
    # 테스트용: 토큰이 'valid-agent-token'이면 결제 승인
    if x_agent_token == "valid-agent-token":
        return True
    
    # 실제 연동 시 Skyfire / AgentKit 등 검증 서버에 확인
    # response = requests.post("https://api.skyfire.xyz/v1/tokens/charge", ...)
    
    raise HTTPException(status_code=402, detail="Payment Required: Invalid agent token")

@app.get("/")
def home():
    return {"message": "AI Agent API Server is Running!"}

@app.get("/api/v1/data", dependencies=[Depends(verify_agent_payment)])
def get_data(symbol: str = "BTC"):
    """
    결제가 확인된 에이전트에만 제공하는 유료 데이터
    """
    return {
        "status": "success",
        "symbol": symbol,
        "price_usd": 95000,
        "signal": "HOLD",
        "message": "Payment verified. Thank you for using the agent API."
    }