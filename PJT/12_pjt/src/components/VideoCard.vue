<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  video: { type: Object, required: true },
})

const router = useRouter()

function goDetail() {
  router.push({ name: 'video-detail', params: { id: props.video.id } })
}
</script>

<template>
  <article class="video-card" @click="goDetail">
    <div class="video-card__thumb">
      <img :src="video.thumbnail" :alt="video.title" />
    </div>
    <div class="video-card__body">
      <h3 class="video-card__title" v-html="video.title"></h3>
      <p class="video-card__channel">{{ video.channelTitle }}</p>
    </div>
  </article>
</template>

<style scoped>
.video-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: transform 0.15s, box-shadow 0.15s;
}
.video-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.video-card__thumb {
  aspect-ratio: 16 / 9;
  background: #e9ebf0;
}
.video-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.video-card__body {
  padding: 12px 14px 16px;
}
.video-card__title {
  font-size: 0.98rem;
  font-weight: 600;
  line-height: 1.35;
  margin: 0 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.video-card__channel {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0;
}
</style>
