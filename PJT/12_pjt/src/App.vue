<script setup>
import NavBar from '@/components/NavBar.vue'
import ChatBot from '@/components/ChatBot.vue'
</script>

<template>
  <NavBar />
  <main>
    <RouterView />
  </main>
  <!-- 심화 F1211: 전역 AI 에이전트 챗봇 -->
  <ChatBot />
</template>
