import { defineStore } from 'pinia'
import { ref } from 'vue'

// 현재 상세 페이지에서 보고 있는 영상/채널 컨텍스트.
// 챗봇의 "이 채널 구독해줘" 같은 명령이 참조한다.
export const useUiStore = defineStore('ui', () => {
  const currentVideo = ref(null)

  function setCurrentVideo(video) {
    currentVideo.value = video
  }
  function clearCurrentVideo() {
    currentVideo.value = null
  }

  return { currentVideo, setCurrentVideo, clearCurrentVideo }
})
