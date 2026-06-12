<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useSearchStore } from '@/stores/search'
import VideoCard from '@/components/VideoCard.vue'

const route = useRoute()
const router = useRouter()
const searchStore = useSearchStore()
const { results, loading, error, hasSearched } = storeToRefs(searchStore)

const keyword = ref(route.query.q ?? searchStore.query ?? '')

function submit() {
  const q = keyword.value.trim()
  if (!q) return
  // URL 쿼리에 검색어 반영 (공유/새로고침 대응)
  router.push({ name: 'search', query: { q } })
  searchStore.runSearch(q)
}

// 챗봇 등 외부에서 ?q= 가 바뀌면 자동 검색
watch(
  () => route.query.q,
  (q) => {
    if (q && q !== searchStore.query) {
      keyword.value = q
      searchStore.runSearch(q)
    }
  },
)

onMounted(() => {
  const q = route.query.q
  if (q && q !== searchStore.query) {
    searchStore.runSearch(q)
  }
})
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back-link">← 뒤로가기</RouterLink>
    <h1 class="page-title">비디오 검색</h1>

    <!-- 검색창 -->
    <div class="search-bar">
      <input
        v-model="keyword"
        type="text"
        placeholder="검색어를 입력하세요"
        @keyup.enter="submit"
      />
      <button @click="submit">찾기</button>
    </div>

    <!-- 상태별 출력 -->
    <p v-if="loading" class="empty-state">검색 중…</p>
    <p v-else-if="error" class="error-box">{{ error }}</p>
    <p v-else-if="hasSearched && results.length === 0" class="empty-state">
      검색 결과가 없습니다.
    </p>

    <div v-if="!loading && results.length" class="video-grid">
      <VideoCard v-for="video in results" :key="video.id" :video="video" />
    </div>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 26px;
}
.search-bar input {
  flex: 1;
  border: 1px solid #d6d9df;
  border-radius: 8px;
  padding: 11px 14px;
  font-size: 0.98rem;
  outline: none;
}
.search-bar input:focus {
  border-color: var(--mt-accent);
}
.search-bar button {
  border: none;
  background: #2ca35f;
  color: #fff;
  border-radius: 8px;
  padding: 0 22px;
  font-weight: 700;
  cursor: pointer;
}
.error-box {
  background: #fdecec;
  color: #c0392b;
  border: 1px solid #f5c6c6;
  border-radius: 8px;
  padding: 14px 16px;
}
</style>
