import requests
from django.conf import settings

def check_inappropriate_content(title, content):
    """
    requests를 사용하여 Upstage Solar 모델을 직접 호출합니다.
    """
    api_key = settings.UPSTAGE_API_KEY
    url = "https://api.upstage.ai/v1/solar/chat/completions" # 직접 호출 주소
    
    if not api_key:
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    아래 게시글에 욕설, 비방, 혐오 표현이 포함되어 있는지 검토해줘. 
    부적절하다면 오직 'True', 문제가 없다면 'False'라고만 대답해.
    제목: {title}
    내용: {content}
    """
    
    data = {
        "model": "solar-1-mini-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=5)
        response.raise_for_status() # 에러 발생 시 예외 발생
        
        result = response.json()
        content_result = result['choices'][0]['message']['content'].strip()
        
        return "True" in content_result
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return False