<script setup>
import { ref } from "vue";
import DocumentationIcon from "./icons/IconDocumentation.vue";
import ToolingIcon from "./icons/IconTooling.vue";
import EcosystemIcon from "./icons/IconEcosystem.vue";
import CommunityIcon from "./icons/IconCommunity.vue";
import SupportIcon from "./icons/IconSupport.vue";
import AIChat from "./AIChat.vue";
import defaultBg from "@/assets/bg/image.png";

const openReadmeInEditor = () => fetch("/__open-in-editor?file=README.md");

// 背景图片URL状态
const backgroundImage = ref(defaultBg);

// 处理背景更新事件
const handleBackgroundUpdate = (imageUrl) => {
  console.log("🎯 收到背景更新事件:", imageUrl);
  console.log("🎯 图片URL类型:", typeof imageUrl);
  console.log("🎯 图片URL长度:", imageUrl ? imageUrl.length : 0);
  
  if (imageUrl) {
    // 测试图片是否可以加载
    const img = new Image();
    img.onload = () => {
      console.log("✅ 图片加载成功，开始更新背景");
      backgroundImage.value = imageUrl;
      console.log("🎨 背景图片已更新为:", backgroundImage.value);
    };
    img.onerror = (error) => {
      console.error("❌ 图片加载失败:", error);
      console.error("❌ 失败的图片URL:", imageUrl);
    };
    img.src = imageUrl;
  } else {
    console.log("⚠️ 警告: 收到空的图片URL");
  }
};
</script>

<template>
  <div class="bg" :style="{ backgroundImage: `url(${backgroundImage})` }"></div>
  <AIChat @backgroundUpdate="handleBackgroundUpdate" />
</template>

<style scoped>
.bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
  z-index: -1;
  transition: background-image 0.5s ease-in-out;
}
.bg::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3); /* 0.5为透明度，可调整 */
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
