<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { parseCommand, isAiEnabled } from '@/api/ai'
import { useSearchStore } from '@/stores/search'
import { useLibraryStore } from '@/stores/library'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const searchStore = useSearchStore()
const library = useLibraryStore()
const ui = useUiStore()

const open = ref(false)
const input = ref('')
const busy = ref(false)
const messages = ref([
  {
    role: 'bot',
    text: '무엇을 도와드릴까요? 예) "삼성전자 검색해줘", "저장한 영상 보여줘", "이 채널 구독해줘"',
  },
])
const logEl = ref(null)

async function scrollToBottom() {
  await nextTick()
  logEl.value?.scrollTo({ top: logEl.value.scrollHeight })
}

function pushBot(text) {
  messages.value.push({ role: 'bot', text })
  scrollToBottom()
}

/**
 * 인텐트를 실제 서비스 기능으로 실행
 */
async function executeIntent(intent) {
  switch (intent.action) {
    case 'search': {
      if (!intent.query) {
        pushBot('검색어를 인식하지 못했어요. "OO 검색해줘"처럼 말씀해 주세요.')
        return
      }
      pushBot(`'${intent.query}' 영상을 검색할게요.`)
      await router.push({ name: 'search', query: { q: intent.query } })
      await searchStore.runSearch(intent.query)
      break
    }
    case 'show_saved':
      pushBot('나중에 볼 영상 목록으로 이동할게요.')
      router.push({ name: 'saved' })
      break
    case 'show_channels':
      pushBot('저장한 채널 목록으로 이동할게요.')
      router.push({ name: 'channels' })
      break
    case 'save_channel': {
      const v = ui.currentVideo
      if (!v?.channelId) {
        pushBot('지금 보고 있는 채널이 없어요. 영상 상세 페이지에서 다시 시도해 주세요.')
        return
      }
      library.saveChannel({ channelId: v.channelId, channelTitle: v.channelTitle })
      pushBot(`'${v.channelTitle}' 채널을 저장했어요.`)
      break
    }
    case 'go_home':
      pushBot('홈으로 이동할게요.')
      router.push({ name: 'home' })
      break
    default:
      pushBot('아직 이해하지 못한 명령이에요. 검색, 저장 목록 보기, 채널 저장 등을 시켜보세요.')
  }
}

async function send() {
  const text = input.value.trim()
  if (!text || busy.value) return

  messages.value.push({ role: 'user', text })
  input.value = ''
  busy.value = true
  scrollToBottom()

  try {
    const { intent, source } = await parseCommand(text)
    console.log('[AI] intent:', intent, 'via', source)
    await executeIntent(intent)
  } catch (e) {
    pushBot('명령 처리 중 오류가 발생했어요: ' + e.message)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <!-- 토글 버튼 -->
  <button class="cb-fab" @click="open = !open" :aria-label="open ? '챗봇 닫기' : '챗봇 열기'">
    {{ open ? '✕' : '🤖' }}
  </button>

  <!-- 챗봇 패널 -->
  <div v-if="open" class="cb-panel">
    <header class="cb-header">
      <span>AI 어시스턴트</span>
      <small class="cb-badge">{{ isAiEnabled ? 'Gemini' : '규칙 기반' }}</small>
    </header>

    <div ref="logEl" class="cb-log">
      <div v-for="(m, i) in messages" :key="i" class="cb-msg" :class="`cb-msg--${m.role}`">
        {{ m.text }}
      </div>
      <div v-if="busy" class="cb-msg cb-msg--bot cb-typing">생각 중…</div>
    </div>

    <div class="cb-input">
      <input
        v-model="input"
        type="text"
        placeholder="명령을 입력하세요"
        @keyup.enter="send"
        :disabled="busy"
      />
      <button @click="send" :disabled="busy">전송</button>
    </div>
  </div>
</template>

<style scoped>
.cb-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: var(--mt-accent);
  color: #fff;
  font-size: 1.4rem;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(47, 107, 255, 0.4);
  z-index: 1000;
}
.cb-panel {
  position: fixed;
  right: 24px;
  bottom: 92px;
  width: 340px;
  max-width: calc(100vw - 32px);
  height: 460px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000;
}
.cb-header {
  background: var(--mt-dark);
  color: #fff;
  padding: 12px 16px;
  font-weight: 700;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cb-badge {
  background: rgba(255, 255, 255, 0.18);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 500;
}
.cb-log {
  flex: 1;
  padding: 14px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #f7f8fa;
}
.cb-msg {
  max-width: 85%;
  padding: 9px 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.4;
  white-space: pre-wrap;
}
.cb-msg--bot {
  align-self: flex-start;
  background: #fff;
  border: 1px solid #e6e8ec;
}
.cb-msg--user {
  align-self: flex-end;
  background: var(--mt-accent);
  color: #fff;
}
.cb-typing {
  opacity: 0.7;
  font-style: italic;
}
.cb-input {
  display: flex;
  gap: 8px;
  padding: 10px;
  border-top: 1px solid #eceef1;
}
.cb-input input {
  flex: 1;
  border: 1px solid #d6d9df;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 0.9rem;
  outline: none;
}
.cb-input input:focus {
  border-color: var(--mt-accent);
}
.cb-input button {
  border: none;
  background: var(--mt-accent);
  color: #fff;
  border-radius: 8px;
  padding: 0 14px;
  font-weight: 600;
  cursor: pointer;
}
.cb-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
