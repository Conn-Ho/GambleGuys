<script setup>
import { ref, onMounted } from 'vue'
import Loading from './components/Loading.vue'
import TheWelcome from './components/TheWelcome.vue'
import AudioStatusMonitor from './components/AudioStatusMonitor.vue'

const loading = ref(true)

onMounted(() => {
  // 模拟加载2秒
  setTimeout(() => {
    loading.value = false
  }, 2000)
})
</script>

<template>
  <Loading v-if="loading" />
  <div v-else>
    <header>
      <div class="header-content">
        <h1>🧠 EEG音乐生成系统</h1>
        <p>实时脑波情绪识别与音乐生成</p>
      </div>
    </header>
    
    <main>
      <AudioStatusMonitor />
      <TheWelcome />
    </main>
  </div>
</template>

<style scoped>
header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 20px;
  text-align: center;
  margin-bottom: 40px;
}

.header-content h1 {
  margin: 0 0 10px 0;
  font-size: 2.5em;
  font-weight: 700;
}

.header-content p {
  margin: 0;
  font-size: 1.2em;
  opacity: 0.9;
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 2em;
  }
  
  .header-content p {
    font-size: 1em;
  }
  
  main {
    padding: 0 10px;
  }
}
</style>
