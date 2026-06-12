import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import SearchView from '@/views/SearchView.vue'
import VideoDetailView from '@/views/VideoDetailView.vue'
import SavedView from '@/views/SavedView.vue'
import ChannelsView from '@/views/ChannelsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      // F1201 - 검색 결과 페이지 (?q=키워드)
      path: '/search',
      name: 'search',
      component: SearchView,
    },
    {
      // F1202 - 동영상 상세 페이지
      path: '/video/:id',
      name: 'video-detail',
      component: VideoDetailView,
      props: true,
    },
    {
      // F1203 - 나중에 볼 영상
      path: '/saved',
      name: 'saved',
      component: SavedView,
    },
    {
      // F1204 - 좋아하는 채널
      path: '/channels',
      name: 'channels',
      component: ChannelsView,
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
