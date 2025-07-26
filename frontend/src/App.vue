<script setup>
import { ref } from 'vue'
import IntroAnimation from './components/IntroAnimation.vue'
import MemoryGuide from './components/MemoryGuide.vue'
import TheWelcome from './components/TheWelcome.vue'

const currentStep = ref('intro') // 从intro动画开始

// 添加调试日志
console.log("🎮 当前步骤:", currentStep.value);

// 处理intro动画完成事件
const handleIntroCompleted = () => {
  console.log("🎬 Intro动画完成，切换到记忆引导");
  currentStep.value = 'memory'
}

// 处理记忆引导完成事件
const handleMemoryGuideCompleted = (memorySettings) => {
  console.log('🧠 用户记忆设置:', memorySettings)
  console.log("🎮 切换到主游戏界面");
  currentStep.value = 'game'
}
</script>

<template>
  <IntroAnimation v-if="currentStep === 'intro'" @completed="handleIntroCompleted" />
  <MemoryGuide v-else-if="currentStep === 'memory'" @completed="handleMemoryGuideCompleted" />
  <main v-else>
    <TheWelcome />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
