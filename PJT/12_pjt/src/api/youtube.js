import axios from 'axios'

// NF1201: API Key는 .env(VITE_YOUTUBE_API_KEY)에서만 읽어오고
// 소스 코드에 하드코딩하지 않는다. .env는 .gitignore로 제외.
const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY

const youtube = axios.create({
  baseURL: 'https://www.googleapis.com/youtube/v3',
})

/**
 * API 에러를 사용자 친화적인 메시지로 변환
 */
function toFriendlyError(error) {
  if (!API_KEY) {
    return new Error('YouTube API 키가 설정되지 않았습니다. .env 파일에 VITE_YOUTUBE_API_KEY를 입력하세요.')
  }
  const status = error.response?.status
  const reason = error.response?.data?.error?.errors?.[0]?.reason
  if (status === 403 && reason === 'quotaExceeded') {
    return new Error('YouTube API 일일 할당량을 초과했습니다. 잠시 후 다시 시도하세요.')
  }
  if (status === 400 || status === 403) {
    return new Error('API 키가 유효하지 않거나 권한이 없습니다. 키 설정을 확인하세요.')
  }
  return new Error('동영상 정보를 불러오지 못했습니다. 네트워크 상태를 확인하세요.')
}

/**
 * F1201 - 키워드로 동영상 검색
 * @param {string} query 검색어
 * @param {number} maxResults 결과 개수
 * @returns {Promise<Array>} 정규화된 영상 목록
 */
export async function searchVideos(query, maxResults = 12) {
  if (!query?.trim()) return []
  try {
    const { data } = await youtube.get('/search', {
      params: {
        part: 'snippet',
        q: query,
        type: 'video',
        maxResults,
        key: API_KEY,
      },
    })

    // 응답(JSON)에서 필요한 데이터만 추출하여 정규화
    return data.items.map((item) => ({
      id: item.id.videoId,
      title: item.snippet.title,
      channelId: item.snippet.channelId,
      channelTitle: item.snippet.channelTitle,
      description: item.snippet.description,
      thumbnail: item.snippet.thumbnails.medium.url,
      publishedAt: item.snippet.publishTime,
    }))
  } catch (error) {
    throw toFriendlyError(error)
  }
}

/**
 * F1202 - 비디오 ID로 상세 정보 조회 (videos 엔드포인트)
 * @param {string} videoId
 * @returns {Promise<Object|null>}
 */
export async function getVideoDetail(videoId) {
  if (!videoId) return null
  try {
    const { data } = await youtube.get('/videos', {
      params: {
        part: 'snippet',
        id: videoId,
        key: API_KEY,
      },
    })

    const item = data.items?.[0]
    if (!item) return null

    return {
      id: item.id,
      title: item.snippet.title,
      channelId: item.snippet.channelId,
      channelTitle: item.snippet.channelTitle,
      description: item.snippet.description,
      thumbnail: item.snippet.thumbnails?.medium?.url ?? '',
      publishedAt: item.snippet.publishedAt,
    }
  } catch (error) {
    throw toFriendlyError(error)
  }
}
