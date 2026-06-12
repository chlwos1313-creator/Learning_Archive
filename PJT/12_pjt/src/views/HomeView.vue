<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const keyword = ref('')

function go() {
  if (!keyword.value.trim()) return
  router.push({ name: 'search', query: { q: keyword.value.trim() } })
}
</script>

<template>
  <div class="page home">
    <div class="hero">
      <h1>관심 종목 영상 검색</h1>
      <p>YouTube에서 관심 종목 관련 영상을 검색하고, 나중에 볼 영상과 채널을 저장하세요.</p>
      <div class="hero__search">
        <input
          v-model="keyword"
          type="text"
          placeholder="예) 삼성전자, 반도체, SSAFY"
          @keyup.enter="go"
        />
        <button @click="go">검색</button>
      </div>
      <p class="hero__hint">오른쪽 아래 🤖 버튼으로 AI 어시스턴트에게 명령할 수도 있어요.</p>
    </div>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 70px 16px;
}
.hero h1 {
  font-weight: 800;
  font-size: 2.4rem;
  margin-bottom: 12px;
}
.hero p {
  color: #6b7280;
  margin-bottom: 28px;
}
.hero__search {
  display: flex;
  gap: 10px;
  max-width: 540px;
  margin: 0 auto;
}
.hero__search input {
  flex: 1;
  border: 1px solid #d6d9df;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 1rem;
  outline: none;
}
.hero__search input:focus {
  border-color: var(--mt-accent);
}
.hero__search button {
  border: none;
  background: var(--mt-accent);
  color: #fff;
  border-radius: 10px;
  padding: 0 26px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
}
.hero__hint {
  margin-top: 20px;
  font-size: 0.9rem;
  color: #98a0ad;
}
</style>
