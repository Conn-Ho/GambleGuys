<script setup>
import DocumentationIcon from './icons/IconDocumentation.vue'
import ToolingIcon from './icons/IconTooling.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import CommunityIcon from './icons/IconCommunity.vue'
import SupportIcon from './icons/IconSupport.vue'
import AIChat from './AIChat.vue'

const openReadmeInEditor = () => fetch('/__open-in-editor?file=README.md')
</script>

<template>
  <div class="bg"></div>
  <AIChat />
</template>

<style scoped>
.bg {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 100vw;
  height: 100vh;
  background: url('@/assets/bg/image.png') no-repeat center center;
  background-size: cover;
  z-index: -1;
}
.bg::after {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8); /* 0.5为透明度，可调整 */
  pointer-events: none; /* 不影响鼠标事件 */
}
.ai-chat {
  position: fixed;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 360px;
  max-height: 70vh;
  
}
</style>
