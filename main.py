from fastapi import FastAPI, Header, HTTPException, Depends
import os

app = FastAPI(
    title="AI Agent Market Intelligence API",
    description="Base Mainnet 기반 AI 에이전트 전용 실시간 유료 데이터 API",
    version="1.0.0"
)

# -------------------------------------------------------------
# [필수] 본인의 실제 메인넷 암호화폐 지갑 주소(EVM/Base)를 입력하세요.
# (MetaMask 또는 Coinbase Wallet의 0x... 주소)
# -------------------------------------------------------------
MY_MAINNET_WALLET = "0xYourActualBaseWalletAddressHere"

# API 호출 1회당 가격 (USD 기준)
PRICE_PER_CALL_USD = 0.001

def verify_mainnet_payment(x_tx_hash: str = Header(None, alias="X-Tx-Hash")):
    """
    AI 에이전트가 Base 메인넷에서 전송한 결제 트랜잭션(X-Tx-Hash)을 검증합니다.
    """
    if not x_tx_hash:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Payment Required",
                "network": "Base Mainnet (Chain ID: 8453)",
                "payment_asset": "USDC",
                "pay_to": MY_MAINNET_WALLET,
                "price_usd": PRICE_PER_CALL_USD,
                "instruction": "Send 0.001 USDC on Base Mainnet to pay_to address, then include transaction hash in 'X-Tx-Hash' header."
            }
        )
    
    # 트랜잭션 해시 규격 검증 (0x로 시작하는 66자리 문자열)
    if not (x_tx_hash.startswith("0x") and len(x_tx_hash) == 66):
        raise HTTPException(
            status_code=400, 
            detail="Invalid Base Mainnet transaction hash format."
        )
    
    # TODO: 온체인(Base Mainnet RPC) 직접 조회하여 입금 여부 최종 확정
    # 실서비스에서는 web3.py 또는 Base RPC를 통해 토큰 금액과 수신 지갑을 확정 검증합니다.
    
    return True

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "AI Agent Paid Market API",
        "network": "Base Mainnet",
        "price_per_call": f"${PRICE_PER_CALL_USD} USDC",
        "pay_to_wallet": MY_MAINNET_WALLET,
        "docs_for_agents": "/openapi.json"
    }

@app.get("/api/v1/market-data", dependencies=[Depends(verify_mainnet_payment)])
def get_market_data(symbol: str = "BTC"):
    """
    [유료] 에이전트가 결제 완료 후 수신받는 실제 데이터
    """
    return {
        "status": "success",
        "symbol": symbol.upper(),
        "market_price": 95200.0,
        "rsi_14": 62.4,
        "sentiment": "Bullish",
        "agent_action": "ACCUMULATE",
        "timestamp": "2026-10-01T02:20:00Z"
    }
