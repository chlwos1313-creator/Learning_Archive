<script setup>
import { storeToRefs } from 'pinia'
import { useLibraryStore } from '@/stores/library'

const library = useLibraryStore()
const { savedChannels } = storeToRefs(library)

function channelUrl(channelId) {
  return `https://www.youtube.com/channel/${channelId}`
}
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back-link">← 뒤로가기</RouterLink>
    <h1 class="page-title">내가 좋아하는 채널</h1>

    <!-- F1204 ⑥: 저장된 채널 없을 때 -->
    <p v-if="savedChannels.length === 0" class="empty-state">등록된 채널 없음</p>

    <ul v-else class="channel-list">
      <li v-for="c in savedChannels" :key="c.channelId" class="channel-item">
        <a :href="channelUrl(c.channelId)" target="_blank" rel="noopener" class="channel-link">
          {{ c.channelTitle }}
        </a>
        <button class="btn-delete" @click="library.removeChannel(c.channelId)">삭제</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.channel-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-width: 620px;
}
.channel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 10px;
  padding: 16px 18px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.channel-link {
  font-weight: 600;
  color: #20242c;
  text-decoration: none;
}
.channel-link:hover {
  color: var(--mt-accent);
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
