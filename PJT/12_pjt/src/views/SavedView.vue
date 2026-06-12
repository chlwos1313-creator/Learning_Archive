<script setup>
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useLibraryStore } from '@/stores/library'

const router = useRouter()
const library = useLibraryStore()
const { savedVideos } = storeToRefs(library)

function goDetail(id) {
  router.push({ name: 'video-detail', params: { id } })
}
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back-link">← 뒤로가기</RouterLink>
    <h1 class="page-title">나중에 볼 동영상</h1>

    <!-- F1203 ⑥: 저장된 영상 없을 때 -->
    <p v-if="savedVideos.length === 0" class="empty-state">등록된 비디오 없음</p>

    <div v-else class="video-grid">
      <article v-for="v in savedVideos" :key="v.id" class="saved-card">
        <div class="saved-card__thumb" @click="goDetail(v.id)">
          <img :src="v.thumbnail" :alt="v.title" />
        </div>
        <div class="saved-card__body">
          <h3 class="saved-card__title" @click="goDetail(v.id)" v-html="v.title"></h3>
          <button class="btn-delete" @click="library.removeVideo(v.id)">삭제</button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.saved-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.saved-card__thumb {
  aspect-ratio: 16 / 9;
  cursor: pointer;
  background: #e9ebf0;
}
.saved-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.saved-card__body {
  padding: 12px 14px 16px;
}
.saved-card__title {
  font-size: 0.96rem;
  font-weight: 600;
  line-height: 1.35;
  margin: 0 0 10px;
  cursor: pointer;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.btn-delete {
  border: none;
  background: #fbe9e9;
  color: #c0392b;
  font-weight: 600;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
}
.btn-delete:hover {
  background: #f5c6c6;
}
</style>
