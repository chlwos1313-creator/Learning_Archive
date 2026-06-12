import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const VIDEOS_KEY = 'mytube_saved_videos'
const CHANNELS_KEY = 'mytube_saved_channels'

function load(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? []
  } catch {
    return []
  }
}

export const useLibraryStore = defineStore('library', () => {
  // ----- 상태: Local Storage에서 초기 로드 -----
  const savedVideos = ref(load(VIDEOS_KEY)) // [{ id, title, thumbnail }]
  const savedChannels = ref(load(CHANNELS_KEY)) // [{ channelId, channelTitle }]

  // ----- 상태 변경 시 Local Storage에 자동 동기화 -----
  watch(savedVideos, (v) => localStorage.setItem(VIDEOS_KEY, JSON.stringify(v)), { deep: true })
  watch(savedChannels, (v) => localStorage.setItem(CHANNELS_KEY, JSON.stringify(v)), { deep: true })

  // ----- F1203: 나중에 볼 영상 -----
  const isVideoSaved = computed(() => (id) => savedVideos.value.some((v) => v.id === id))

  function saveVideo(video) {
    if (isVideoSaved.value(video.id)) return
    savedVideos.value.push({
      id: video.id,
      title: video.title,
      thumbnail: video.thumbnail,
    })
  }

  function removeVideo(id) {
    savedVideos.value = savedVideos.value.filter((v) => v.id !== id)
  }

  // 저장/저장취소 토글 (상세 페이지 버튼용)
  function toggleVideo(video) {
    isVideoSaved.value(video.id) ? removeVideo(video.id) : saveVideo(video)
  }

  // ----- F1204: 좋아하는 채널 -----
  const isChannelSaved = computed(() => (channelId) =>
    savedChannels.value.some((c) => c.channelId === channelId),
  )

  function saveChannel(channel) {
    if (isChannelSaved.value(channel.channelId)) return
    savedChannels.value.push({
      channelId: channel.channelId,
      channelTitle: channel.channelTitle,
    })
  }

  function removeChannel(channelId) {
    savedChannels.value = savedChannels.value.filter((c) => c.channelId !== channelId)
  }

  function toggleChannel(channel) {
    isChannelSaved.value(channel.channelId)
      ? removeChannel(channel.channelId)
      : saveChannel(channel)
  }

  return {
    savedVideos,
    savedChannels,
    isVideoSaved,
    saveVideo,
    removeVideo,
    toggleVideo,
    isChannelSaved,
    saveChannel,
    removeChannel,
    toggleChannel,
  }
})
