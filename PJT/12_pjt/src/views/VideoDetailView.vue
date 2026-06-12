<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { getVideoDetail } from '@/api/youtube'
import { useLibraryStore } from '@/stores/library'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const library = useLibraryStore()
const ui = useUiStore()
const { isVideoSaved, isChannelSaved } = storeToRefs(library)

const video = ref(null)
const loading = ref(false)
const error = ref('')

const embedUrl = computed(() =>
  video.value ? `https://www.youtube.com/embed/${video.value.id}` : '',
)

async function load(id) {
  loading.value = true
  error.value = ''
  video.value = null
  try {
    const data = await getVideoDetail(id)
    if (!data) {
      error.value = '영상을 찾을 수 없습니다.'
    } else {
      video.value = data
      // 챗봇이 "이 채널 구독해줘" 명령을 처리할 수 있도록 컨텍스트 등록
      ui.setCurrentVideo(data)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// route.params.id 로 비디오 ID를 가져온다 (F1202 ④)
onMounted(() => load(route.params.id))
watch(() => route.params.id, (id) => id && load(id))
onUnmounted(() => ui.clearCurrentVideo())

// F1203: 동영상 저장/취소
function toggleVideo() {
  library.toggleVideo(video.value)
}
// F1204: 채널 저장/취소
function toggleChannel() {
  library.toggleChannel({
    channelId: video.value.channelId,
    channelTitle: video.value.channelTitle,
  })
}
</script>

<template>
  <div class="page">
    <RouterLink to="/search" class="back-link">← 뒤로가기</RouterLink>

    <p v-if="loading" class="empty-state">불러오는 중…</p>
    <p v-else-if="error" class="error-box">{{ error }}</p>

    <template v-else-if="video">
      <h1 class="detail-title" v-html="video.title"></h1>
      <p class="detail-meta">
        업로드 날짜: {{ new Date(video.publishedAt).toLocaleDateString('ko-KR') }}
      </p>

      <!-- F1202: iframe 재생 -->
      <div class="player">
        <iframe
          :src="embedUrl"
          title="YouTube video player"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>

      <!-- 채널 정보 + F1204 채널 저장 -->
      <div class="channel-row">
        <span class="channel-name">{{ video.channelTitle }}</span>
        <button
          class="btn-channel"
          :class="{ active: isChannelSaved(video.channelId) }"
          @click="toggleChannel"
        >
          {{ isChannelSaved(video.channelId) ? '채널 저장 취소' : '채널 저장' }}
        </button>
      </div>

      <!-- 설명 -->
      <p class="detail-desc">{{ video.description || '설명이 없습니다.' }}</p>

      <!-- F1203 동영상 저장 -->
      <button
        class="btn-save"
        :class="{ active: isVideoSaved(video.id) }"
        @click="toggleVideo"
      >
        {{ isVideoSaved(video.id) ? '저장 취소' : '동영상 저장' }}
      </button>
    </template>
  </div>
</template>

<style scoped>
.detail-title {
  font-weight: 800;
  font-size: 1.7rem;
  margin: 6px 0 4px;
}
.detail-meta {
  color: #98a0ad;
  font-size: 0.9rem;
  margin-bottom: 16px;
}
.player {
  position: relative;
  width: 100%;
  max-width: 760px;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
  margin-bottom: 18px;
}
.player iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.channel-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}
.channel-name {
  font-weight: 700;
  font-size: 1.05rem;
}
.btn-channel {
  border: none;
  background: var(--mt-channel);
  color: #4a3500;
  font-weight: 700;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
}
.btn-channel.active {
  background: #e0e3e8;
  color: #5a6373;
}
.detail-desc {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #3c4250;
  max-width: 760px;
  margin-bottom: 22px;
}
.btn-save {
  border: none;
  background: var(--mt-accent);
  color: #fff;
  font-weight: 700;
  border-radius: 8px;
  padding: 10px 22px;
  cursor: pointer;
}
.btn-save.active {
  background: #e0e3e8;
  color: #5a6373;
}
.error-box {
  background: #fdecec;
  color: #c0392b;
  border: 1px solid #f5c6c6;
  border-radius: 8px;
  padding: 14px 16px;
}
</style>
