<template>
  <div class="intro-overlay" v-if="visible">
    <!-- 第一个视频 -->
    <video 
      v-if="currentVideoIndex === 0"
      ref="video1"
      class="intro-video"
      :src="videoSources[0]"
      @ended="nextVideo"
      autoplay
      muted
      playsinline
    ></video>

    <!-- 第二个视频 -->
    <video 
      v-if="currentVideoIndex === 1"
      ref="video2"
      class="intro-video"
      :src="videoSources[1]"
      @ended="nextVideo"
      autoplay
      muted
      playsinline
    ></video>

    <!-- 第三个视频 -->
    <video 
      v-if="currentVideoIndex === 2"
      ref="video3"
      class="intro-video"
      :src="videoSources[2]"
      @ended="nextVideo"
      autoplay
      muted
      playsinline
    ></video>

    <!-- 跳过按钮 -->
    <button class="skip-button" @click="skipIntro">
      {{ currentVideoIndex < videoSources.length - 1 ? '跳过' : '进入游戏' }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import intro1Video from '@/assets/intro/intro1.mp4';
import intro2Video from '@/assets/intro/intro2.mp4';
import intro3Video from '@/assets/intro/intro3.mp4';

// 定义emits
const emit = defineEmits(['completed']);

const visible = ref(true);
const currentVideoIndex = ref(0);

// 视频源文件
const videoSources = [
  intro1Video,
  intro2Video,
  intro3Video
];

// 切换到下一个视频
const nextVideo = () => {
  currentVideoIndex.value++;
  if (currentVideoIndex.value >= videoSources.length) {
    // 所有视频播放完成
    completeIntro();
  }
};

// 跳过intro
const skipIntro = () => {
  if (currentVideoIndex.value < videoSources.length - 1) {
    // 如果不是最后一个视频，进入下一个视频
    nextVideo();
  } else {
    // 如果是最后一个视频，完成intro
  completeIntro();
  }
};

// 完成intro
const completeIntro = () => {
  visible.value = false;
  emit('completed');
};

onMounted(() => {
  // 组件挂载时开始播放第一个视频
  console.log('Intro animation started');
});
</script>

<style scoped>
.intro-overlay {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: #000;
  z-index: 9999;
  overflow: hidden;
}

.intro-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.skip-button {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  z-index: 10000;
}

.skip-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateX(-50%) translateY(-2px);
}

.skip-button:active {
  transform: translateX(-50%) translateY(0);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .skip-button {
    bottom: 20px;
    padding: 10px 16px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .skip-button {
    bottom: 15px;
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style> 