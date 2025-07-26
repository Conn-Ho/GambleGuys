<template>
  <div :class="['loading-container', { 'loading-overlay': !inline, 'loading-inline': inline }]">
    <div class="spinner" :class="{ 'spinner-small': inline }"></div>
    <div class="loading-text" :class="{ 'text-small': inline }">{{ text || '加载中，请稍候...' }}</div>
  </div>
</template>

<script setup>
// 定义props
const props = defineProps({
  inline: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: '加载中，请稍候...'
  }
});
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-overlay {
  position: fixed;
  left: 0; 
  top: 0; 
  right: 0; 
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 9999;
}

.loading-inline {
  position: relative;
  padding: 20px;
  background: transparent;
  z-index: 1;
}

.spinner {
  border: 6px solid rgba(255, 255, 255, 0.3);
  border-top: 6px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.spinner {
  width: 48px;
  height: 48px;
}

.spinner-small {
  width: 32px;
  height: 32px;
  border-width: 4px;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #fff;
  font-size: 18px;
  letter-spacing: 2px;
  text-align: center;
}

.text-small {
  font-size: 14px;
  letter-spacing: 1px;
}
</style>