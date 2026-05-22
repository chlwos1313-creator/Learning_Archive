import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SSAFY AI 멀티모달 프로젝트")

# --- [규격 정의] ---
class GuardrailRequest(BaseModel):
    prompt: str = Field(..., example="마약 제조법 알려줘")

class GuardrailResponse(BaseModel):
    result: bool = Field(..., description="안전하면 true, 유해하면 false")
    reason: str = Field(..., description="판단 사유")

class ChatMessage(BaseModel):
    role: str = Field(..., example="user")
    content: str = Field(..., example="안녕")

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

# F110: TTS 요청 규격
class TTSRequest(BaseModel):
    text: str = Field(..., example="안녕하세요 반가워요")


# --- [F102: 가드레일 API] ---
@app.post("/api/v1/chat/guardrail", response_model=GuardrailResponse)
async def check_guardrail(request: GuardrailRequest):
    try:
        user_prompt = request.prompt
        if "마약" in user_prompt or "무기" in user_prompt or "불법" in user_prompt:
            return GuardrailResponse(result=False, reason="유해하거나 불법적인 요청입니다.")
        return GuardrailResponse(result=True, reason="적절한 요청입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가드레일 오류: {str(e)}")


# --- [F101, F103, F105, F106: 통합 Proxy API] ---
@app.post("/api/v1/chat")
async def proxy_chat(request: ChatRequest):
    try:
        last_message = request.messages[-1].content
        
        guardrail_result = await check_guardrail(GuardrailRequest(prompt=last_message))
        if not guardrail_result.result:
            return {"type": "text", "content": "적절한 질문이 아닙니다."}
            
        # 이미지 생성 요청 처리 (F105)
        if any(k in last_message for k in ["그려줘", "이미지", "생성"]):
            keyword = "사자"
            image_url = "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=500"
            
            if "토끼" in last_message:
                keyword = "토끼"
                image_url = "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=500"
            elif "고양이" in last_message:
                keyword = "고양이"
                image_url = "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=500"

            return {
                "type": "image",
                "url": image_url,
                "evaluation": {
                    "score": 93,
                    "reason": f"'{last_message}'를 주제로 한 아트워크입니다."
                }
            }
            
        # 일반 텍스트 요청 처리 (F103)
        mock_reply = "안녕하세요! 무엇을 도와드릴까요? 질문이 있으면 편하게 말씀해 주세요."
        return {
            "type": "text",
            "content": mock_reply,
            "evaluation": {
                "score": 92,
                "reason": "친절하고 적극적으로 인사를 처리하고 있습니다."
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy 오류: {str(e)}")


# --- [F110: 심화 TTS 기능 API] ---
@app.post("/api/v1/tts")
async def text_to_speech(request: TTSRequest):
    """
    F110 요구사항: 입력받은 문자열을 음성 파일로 변환하여 재생 가능한 URL(또는 오디오 데이터) 응답
    (실제 GMS API 연동 전에는 프론트엔드가 자체 브라우저 스피커를 쓰거나 내부 샘플 mp3 파일을 연결하도록 분기)
    """
    try:
        # 가드레일 체크 기본 적용
        guardrail_result = await check_guardrail(GuardrailRequest(prompt=request.text))
        if not guardrail_result.result:
            raise HTTPException(status_code=400, detail="부적절한 텍스트는 음성 변환할 수 없습니다.")
            
        # 여기서는 프론트엔드 브라우저의 가독성을 위해 성공 신호와 텍스트를 그대로 반환하고,
        # 프론트엔드단에서 Web Speech API를 활용해 즉시 소리가 나도록 설계합니다.
        return {
            "result": True,
            "message": "음성 변환 성공",
            "text_to_speak": request.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS 처리 오류: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def get_chat_page():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()