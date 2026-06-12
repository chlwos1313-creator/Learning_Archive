import axios from 'axios'

// F1211 심화: 생성형 AI(Gemini)를 활용한 명령 분류기.
// 사용자의 자연어 입력을 아래 인텐트(JSON)로 변환한다.
//
// 지원 인텐트:
//   { "action": "search",        "query": "검색어" }
//   { "action": "show_saved" }
//   { "action": "show_channels" }
//   { "action": "save_channel" }   // 현재 보고 있는 상세 페이지의 채널 저장
//   { "action": "go_home" }
//   { "action": "unknown" }

const GEMINI_KEY = import.meta.env.VITE_GEMINI_API_KEY
const GEMINI_MODEL = import.meta.env.VITE_GEMINI_MODEL || 'gemini-2.0-flash'

const SYSTEM_PROMPT = `너는 "관심 종목 영상 검색 서비스(MyTube)"의 명령 분류기다.
사용자의 한국어/영어 입력을 분석해 아래 JSON 형식 하나만 출력한다.
설명, 마크다운, 코드펜스 없이 순수 JSON만 출력한다.

가능한 action:
- "search": 영상을 검색할 때. query에 검색 키워드만 깔끔히 추출.
  예) "삼성전자 영상 찾아줘" -> {"action":"search","query":"삼성전자"}
  예) "SSAFY 검색해줘" -> {"action":"search","query":"SSAFY"}
- "show_saved": 저장한/나중에 볼 영상을 보여달라고 할 때.
- "show_channels": 저장한 채널/구독 목록을 보여달라고 할 때.
- "save_channel": 지금 보는 채널을 저장/구독하라고 할 때.
- "go_home": 홈/처음으로 가달라고 할 때.
- "unknown": 위에 해당하지 않을 때.

반드시 위 형식의 JSON 한 줄만 출력한다.`

/**
 * 규칙 기반 폴백 파서 (Gemini 키가 없거나 호출 실패 시)
 */
function ruleBasedParse(text) {
  const t = text.trim().toLowerCase()

  if (/(저장한|나중에|찜한).*(영상|비디오|동영상)|saved/.test(t)) {
    return { action: 'show_saved' }
  }
  if (/(저장한|구독한|좋아하는).*채널|채널.*(목록|보여)|channels?/.test(t)) {
    return { action: 'show_channels' }
  }
  if (/(이|현재|지금).*채널.*(저장|구독)|채널.*(저장|구독)해/.test(t)) {
    return { action: 'save_channel' }
  }
  if (/(홈|처음|메인).*(가|이동|보여)|go ?home|home/.test(t)) {
    return { action: 'go_home' }
  }

  // 검색 의도: "X 검색/찾아/검색해줘" 패턴에서 키워드 추출
  const searchMatch = text.match(
    /(.+?)\s*(을|를|에 대한|관련)?\s*(영상\s*)?(검색|찾아|찾아줘|검색해줘|검색해|보여줘)/,
  )
  if (searchMatch && searchMatch[1].trim()) {
    return { action: 'search', query: searchMatch[1].replace(/['"]/g, '').trim() }
  }

  // 명령 키워드가 없으면 입력 전체를 검색어로 간주
  if (text.trim()) {
    return { action: 'search', query: text.trim() }
  }
  return { action: 'unknown' }
}

/**
 * Gemini API로 자연어 명령을 인텐트 JSON으로 변환
 */
async function geminiParse(text) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_KEY}`

  const { data } = await axios.post(
    url,
    {
      systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
      contents: [{ role: 'user', parts: [{ text }] }],
      generationConfig: {
        temperature: 0,
        responseMimeType: 'application/json',
      },
    },
    { headers: { 'Content-Type': 'application/json' } },
  )

  const raw = data.candidates?.[0]?.content?.parts?.[0]?.text ?? ''
  const cleaned = raw.replace(/```json|```/g, '').trim()
  return JSON.parse(cleaned)
}

/**
 * 자연어 명령 -> 인텐트.
 * Gemini 키가 있으면 AI로, 없거나 실패하면 규칙 기반으로 분류한다.
 * @param {string} text 사용자 입력
 * @returns {Promise<{intent: object, source: 'gemini'|'rule'}>}
 */
export async function parseCommand(text) {
  if (GEMINI_KEY) {
    try {
      const intent = await geminiParse(text)
      return { intent, source: 'gemini' }
    } catch (e) {
      console.warn('[AI] Gemini 호출 실패, 규칙 기반으로 대체:', e.message)
    }
  }
  return { intent: ruleBasedParse(text), source: 'rule' }
}

export const isAiEnabled = Boolean(GEMINI_KEY)
