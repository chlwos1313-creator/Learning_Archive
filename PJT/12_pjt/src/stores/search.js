import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchVideos } from '@/api/youtube'

export const useSearchStore = defineStore('search', () => {
  const query = ref('')
  const results = ref([])
  const loading = ref(false)
  const error = ref('')
  const hasSearched = ref(false)

  async function runSearch(keyword) {
    const q = (keyword ?? query.value).trim()
    if (!q) return
    query.value = q
    loading.value = true
    error.value = ''
    hasSearched.value = true
    try {
      results.value = await searchVideos(q)
    } catch (e) {
      error.value = e.message
      results.value = []
    } finally {
      loading.value = false
    }
  }

  return { query, results, loading, error, hasSearched, runSearch }
})
