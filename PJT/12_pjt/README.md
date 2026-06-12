# 12_pjt · 관심 종목 영상 검색 서비스 (MyTube)

YouTube Data API v3와 Vue 3로 구현한 관심 종목 영상 검색 · 시청 · 저장 SPA.
검색 → 시청 → 저장의 전체 사용자 흐름과, 생성형 AI 기반 명령 에이전트(심화)를 제공한다.

## 기술 스택

- Vue 3 (`<script setup>` Composition API)
- Vue Router 4 / Pinia 2
- Axios (비동기 통신)
- Bootstrap 5 (반응형 베이스)
- YouTube Data API v3 / Gemini API (심화)

## 시작하기

```bash
# 1. 의존성 설치
npm install

# 2. 환경 변수 설정
cp .env.example .env
#   .env 파일을 열어 키를 입력
#   VITE_YOUTUBE_API_KEY=발급받은_유튜브_키
#   VITE_GEMINI_API_KEY=(선택) 챗봇용 Gemini 키

# 3. 개발 서버 실행
npm run dev
```

### API Key 발급 (NF1201)

1. Google Cloud Console → 라이브러리 → **YouTube Data API v3** 사용
2. 사용자 인증 정보 → API 키 생성 후 복사
3. `.env`의 `VITE_YOUTUBE_API_KEY`에 입력
4. `.env`는 `.gitignore`에 포함되어 키가 저장소에 노출되지 않는다.

## 구현 기능

### 기본 기능 (필수)

| 번호 | 기능 | 구현 위치 |
| --- | --- | --- |
| F1201 | 동영상 검색 결과 출력 | `views/SearchView.vue`, `components/VideoCard.vue`, `api/youtube.js` |
| F1202 | 동영상 상세 정보(iframe 재생) | `views/VideoDetailView.vue` |
| F1203 | 나중에 볼 영상 저장/삭제 | `views/SavedView.vue`, `stores/library.js` |
| F1204 | 좋아하는 채널 저장/삭제 | `views/ChannelsView.vue`, `stores/library.js` |

- **F1201**: 네비게이션 바 `Search`에서 키워드 입력(Enter/버튼) → `/youtube/v3/search` 호출 → 썸네일·제목·채널명을 카드 그리드로 출력. 카드 클릭 시 상세 페이지로 이동.
- **F1202**: `/video/:id`에서 `route.params.id`로 비디오 ID를 받아 `/youtube/v3/videos` 호출. iframe 재생 + 제목·채널명·설명 표시.
- **F1203**: 저장 버튼 → Local Storage에 `id/title/thumbnail` 저장, 저장 시 버튼이 "저장 취소"로 토글. `/saved`에서 목록·삭제, 비어 있으면 "등록된 비디오 없음" 표시.
- **F1204**: 상세 페이지 채널명 옆 "채널 저장" → Local Storage에 `channelId/channelTitle` 저장. `/channels`에서 목록·삭제, 비어 있으면 "등록된 채널 없음" 표시.

### 심화 기능 (선택) — F1211 AI 에이전트 챗봇

오른쪽 아래 🤖 버튼으로 여는 챗봇에 자연어로 명령하면 실제 서비스 기능이 실행된다.

- 명령 분류: `api/ai.js`의 `parseCommand()`가 입력을 인텐트 JSON으로 변환한 뒤 `ChatBot.vue`의 `executeIntent()`가 라우팅/스토어 액션을 실행.
- Gemini 키가 있으면 Gemini로, 없으면 내장 **규칙 기반 파서**로 동작(키 없이도 데모 가능).

| 사용자 발화 | 인텐트 | 동작 |
| --- | --- | --- |
| "SSAFY 검색해줘" | `search` | `/search`로 이동 후 검색 실행 |
| "저장한 영상 보여줘" | `show_saved` | `/saved` 이동 |
| "저장한 채널 보여줘" | `show_channels` | `/channels` 이동 |
| "이 채널 구독해줘" | `save_channel` | 현재 상세 페이지 채널 저장 |
| "홈으로 가줘" | `go_home` | `/` 이동 |

명령어/기능은 `api/ai.js`의 프롬프트와 `ChatBot.vue`의 `executeIntent` 분기에서 자유롭게 확장 가능.

## 폴더 구조

```
src/
├── api/
│   ├── youtube.js   # 검색/상세 API + 에러 처리
│   └── ai.js        # Gemini 명령 분류 + 규칙 기반 폴백
├── stores/
│   ├── library.js   # 저장 영상/채널 (Local Storage 동기화)
│   ├── search.js    # 검색 상태
│   └── ui.js        # 현재 상세 영상 컨텍스트
├── components/
│   ├── NavBar.vue
│   ├── VideoCard.vue
│   └── ChatBot.vue  # 심화 AI 에이전트
├── views/
│   ├── HomeView.vue
│   ├── SearchView.vue
│   ├── VideoDetailView.vue
│   ├── SavedView.vue
│   └── ChannelsView.vue
└── router/index.js
```

## 학습 내용 / 어려웠던 점 / 개선점

- **학습 내용**: Vue 3 컴포넌트 분리(NF1203), Axios 비동기 처리, Pinia ↔ Local Storage 동기화(`watch` + `deep`), 라우트 파라미터/쿼리 기반 데이터 로딩, 생성형 AI 명령 분류.
- **어려웠던 점**: YouTube API 응답 구조 정규화(search는 `id.videoId`, videos는 `id`로 형태가 다름), API 할당량(quota) 에러 핸들링.
- **개선점**: 검색 결과 페이지네이션(`nextPageToken`), 댓글/관련 영상, 챗봇 멀티턴 대화, 채널 영상 모아보기.

## 산출물

- 구현 소스 코드 (`node_modules` 제외 압축)
- 각 요구사항 실행 결과 캡처본
- 본 README.md
- GitLab 업로드 (프로젝트명 `12_pjt`)
