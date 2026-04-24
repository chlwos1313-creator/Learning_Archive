"""
OpenAI/Upstage Chat Completions로 부적절한 텍스트 검사 및 투자 성향 분석.
"""
from django.conf import settings
from openai import OpenAI

SYSTEM_PROMPT = """당신은 한국어 커뮤니티의 '부적절 표현' 판별기입니다.
아래 규칙으로 사용자 입력(한 문장 또는 여러 문장)을 검사하세요.

[판정 원칙]
1) 아래 항목 중 하나라도 해당하면 반드시 부적절(YES)입니다.
2) 맥락상 상대를 직접 공격/비하/모욕하면, 전형적 욕설이 아니어도 YES입니다.
3) 우회 표현(오타, 띄어쓰기 분리, 초성/자모 분해, 비슷한 발음 치환)도 원형으로 간주해 YES 처리합니다.

[YES(부적절)로 판단할 내용]
- 욕설/비속어/모욕/인신공격: 예) "멍청아", "나쁜 새끼야", "한심한 놈", "병X", "ㅂㅅ", "ㅅㅂ" 등
- 혐오/차별/비하 발언: 성별, 지역, 인종, 장애, 종교, 직업군 등에 대한 멸시/배제
- 괴롭힘/협박/위협/폭력 조장: 해치겠다는 표현, 위해 유도, 자해·타해 선동
- 성적 대상화/성희롱/음란성 표현
- 악의적 비방/모욕적 조롱/지속적 괴롭힘 맥락

[우회 표현 처리 규칙]
- 욕설 사이에 공백/특수문자 삽입: 예) "ㅅ ㅂ", "ㅂ-ㅅ", "새.끼"
- 초성/자모/은어/오타/변형: 예) "ㅁㅊ", "ㅂㅅ", "새기", "시@발" 등
- 반복 문자나 늘임표로 완화한 형태도 동일하게 간주

[NO(적절) 예시]
- 금융 자산, 투자 의견, 시장 분석, 일반 질문, 중립적 비판
- 감정 표현이 있어도 타인 모욕/혐오/폭력/성적 괴롭힘이 없는 경우

출력 규칙:
- 부적절하면 YES
- 적절하면 NO
- 반드시 YES 또는 NO만 단독으로 출력 (설명/부연/구두점/이모지 금지)"""


def _build_llm_client():
    """
    사용자가 제공한 Upstage (solar-pro3) 설정을 적용합니다.
    """
    client = OpenAI(
        api_key="up_qVl5yEKdGy7vRfIsiKScygdmrjs7O",
        base_url="https://api.upstage.ai/v1"
    )
    return client, "solar-pro3"


def is_inappropriate(text: str) -> bool:
    """
    텍스트에 부적절한 내용이 있으면 True 반환.
    MODE(OPENAI/UPSTAGE)에 맞는 API 키가 있을 때만 Chat Completions로 판별.
    """
    if not text or not text.strip():
        return False

    client, model = _build_llm_client()
    if not client:
        return False

    stripped = text.strip()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": stripped},
            ],
            stream=False,
            temperature=0, # 판별기는 일관된 결과를 위해 0 유지
            max_tokens=65536,
        )
        answer = (resp.choices[0].message.content or "").strip().upper()
        print(f"부적절 단어 검사 결과 = {answer}")
        return "YES" in answer
    except Exception as e:
        print(f"[LLM 부적절 검사 실패] {type(e).__name__}: {e}")
        return False


def analyze_investment_style(posts_text: str) -> str:
    """
    사용자가 작성한 게시글들을 기반으로 투자 성향을 분석합니다.
    """
    if not posts_text or not posts_text.strip():
        return "작성한 게시글이 없어 투자 성향을 분석할 수 없습니다."

    client, model = _build_llm_client()
    if not client:
        return "LLM API 설정이 올바르지 않아 분석할 수 없습니다."

    analysis_prompt = """
    당신은 전문 투자 분석가입니다. 
    다음은 한 사용자가 금융 자산 커뮤니티에 작성한 게시글들의 모음입니다.
    이 게시글들을 분석하여 사용자의 주된 '투자 성향'을 요약하여 알려주세요.
    예를 들면 '가치투자자', '단기트레이더', '안전제일주의', '하이리스크 테이커' 등 적절한 키워드와 함께 이유를 3~4문장으로 친절하게 설명해주세요.
    마크다운 형식을 적절히 사용하여 읽기 좋게 구성해주세요.
    """
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": posts_text},
            ],
            stream=False,
            temperature=0.8,
            max_tokens=65536,
            reasoning_effort="medium"
        )
        answer = (resp.choices[0].message.content or "").strip()
        return answer
    except Exception as e:
        print(f"[LLM 투자 성향 분석 실패] {type(e).__name__}: {e}")
        return "투자 성향 분석 중 오류가 발생했습니다. 나중에 다시 시도해 주세요."
