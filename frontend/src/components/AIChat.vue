<template>
  <div class="chat-container">
    <!-- 动态模糊光圈 -->
    <div 
      class="dream-aura"
      :style="dreamAuraStyle"
    ></div>
    
    <!-- 角色图片层 -->
    <div class="character-layer">
      <img
        :src="currentCharacterImage"
        alt="角色图片"
        class="character-image"
        v-if="currentCharacterImage"
      />
    </div>

    <!-- 故事状态显示 -->
    <div class="story-status" v-if="storyState.scene_count > 0">
     
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${(storyState.scene_count % 10) * 10}%` }"
        ></div>
      </div>
    </div>

    <!-- 对话历史显示区域 -->
    <div class="chat-history" v-if="showChatHistory">
      <div class="chat-messages">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          class="message-wrapper"
          :class="message.role"
        >
          <div class="message-bubble">
            <p class="message-text">{{ message.text }}</p>
            <span class="message-time">{{ formatTime(new Date()) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI回复对话框 (只显示最新的一个，透明样式，位置在输入框上方，居中) -->
    <div
      v-if="latestAiMessage && !showChatHistory"
      class="ai-dialog-wrapper"
      style="position: fixed; bottom: 140px; left: 50%; transform: translateX(-50%); display: flex; justify-content: center; pointer-events: none; z-index: 10;"
    >
      <div class="ai-dialog" style="pointer-events: auto;">
        <div class="ai-dialog-content">
          <p class="ai-response">{{ latestAiMessage.text }}</p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrapper">
      <Loading :inline="true" text="正在思考..." />
    </div>

  

  

    <!-- 聊天切换按钮 -->
    <!-- <div class="chat-controls">
      <button 
        @click="toggleChatHistory" 
        class="chat-toggle-btn"
        :class="{ active: showChatHistory }"
      >
        {{ showChatHistory ? "隐藏对话" : "查看对话" }}
      </button>
    </div> -->

    <!-- 简单输入框 -->
    <div class="simple-input-container">
      <div class="input-wrapper">
        <input
          v-model="input"
          @keyup.enter="handleSend"
          placeholder="输入你的想法..."
          :disabled="loading"
          class="story-input"
        />
        <button
          @click="handleSend"
          :disabled="loading || !input.trim()"
          class="send-button"
        >
          {{ loading ? "发送中..." : "发送" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed, watch } from "vue";
import Loading from './Loading.vue';

// 定义发射事件
const emit = defineEmits(["backgroundUpdate"]);

const input = ref("");
const loading = ref(false);
const showChatHistory = ref(false);
const showAuraPanel = ref(false);
const currentThemeIndex = ref(0);

// 动态模糊光圈控制
const dreamAuraConfig = ref({
  // 颜色配置 (RGBA)
  colors: [
    'rgba(138, 43, 226, 0.3)',   // 紫色
    'rgba(75, 0, 130, 0.25)',    // 靛蓝
    'rgba(72, 61, 139, 0.3)',    // 深紫
    'rgba(147, 112, 219, 0.25)', // 中紫
    'rgba(123, 104, 238, 0.3)'   // 淡紫
  ],
  // 波动强度 (0-1)
  intensity: 0.6,
  // 动画速度 (秒)
  animationSpeed: 8,
  // 模糊程度 (px)
  blurAmount: 80,
  // 大小变化范围
  sizeRange: { min: 200, max: 400 }
});

// 计算动态光圈样式
const dreamAuraStyle = computed(() => {
  const config = dreamAuraConfig.value;
  return {
    '--aura-color-1': config.colors[0],
    '--aura-color-2': config.colors[1], 
    '--aura-color-3': config.colors[2],
    '--aura-color-4': config.colors[3],
    '--aura-color-5': config.colors[4],
    '--aura-intensity': config.intensity,
    '--aura-speed': `${config.animationSpeed}s`,
    '--aura-blur': `${config.blurAmount}px`,
    '--aura-size-min': `${config.sizeRange.min}px`,
    '--aura-size-max': `${config.sizeRange.max}px`
  };
});

// 颜色主题数据
const colorThemes = ref([
  {
    name: '神秘紫',
    preview: 'linear-gradient(45deg, #8A2BE2, #4B0082)',
    colors: [
      'rgba(138, 43, 226, 0.3)',
      'rgba(75, 0, 130, 0.25)', 
      'rgba(72, 61, 139, 0.3)',
      'rgba(147, 112, 219, 0.25)',
      'rgba(123, 104, 238, 0.3)'
    ]
  },
  {
    name: '梦幻蓝',
    preview: 'linear-gradient(45deg, #1E90FF, #0064C8)',
    colors: [
      'rgba(30, 144, 255, 0.3)',
      'rgba(0, 100, 200, 0.25)',
      'rgba(65, 105, 225, 0.3)', 
      'rgba(70, 130, 180, 0.25)',
      'rgba(100, 149, 237, 0.3)'
    ]
  },
  {
    name: '魔法绿',
    preview: 'linear-gradient(45deg, #00FF7F, #2E7D32)',
    colors: [
      'rgba(0, 255, 127, 0.3)',
      'rgba(46, 125, 50, 0.25)',
      'rgba(0, 150, 136, 0.3)',
      'rgba(76, 175, 80, 0.25)', 
      'rgba(129, 199, 132, 0.3)'
    ]
  },
  {
    name: '温暖橙',
    preview: 'linear-gradient(45deg, #FF8C00, #FF4500)',
    colors: [
      'rgba(255, 140, 0, 0.3)',
      'rgba(255, 69, 0, 0.25)',
      'rgba(255, 165, 0, 0.3)',
      'rgba(255, 215, 0, 0.25)',
      'rgba(255, 193, 7, 0.3)'
    ]
  },
  {
    name: '神秘红',
    preview: 'linear-gradient(45deg, #DC143C, #8B0000)',
    colors: [
      'rgba(220, 20, 60, 0.3)',
      'rgba(139, 0, 0, 0.25)',
      'rgba(178, 34, 34, 0.3)',
      'rgba(205, 92, 92, 0.25)',
      'rgba(240, 128, 128, 0.3)'
    ]
  }
]);

// 更改光圈配置的方法
const updateAuraConfig = (newConfig) => {
  dreamAuraConfig.value = { ...dreamAuraConfig.value, ...newConfig };
};

// 切换光圈控制面板
const toggleAuraPanel = () => {
  showAuraPanel.value = !showAuraPanel.value;
};

// 设置颜色主题
const setColorTheme = (themeIndex) => {
  currentThemeIndex.value = themeIndex;
  const theme = colorThemes.value[themeIndex];
  updateAuraConfig({ colors: theme.colors });
  console.log(`🎨 切换到颜色主题: ${theme.name}`);
};

// 应用预设
const applyPreset = (presetName) => {
  const presets = {
    gentle: {
      intensity: 0.3,
      animationSpeed: 12,
      blurAmount: 60,
      sizeRange: { min: 150, max: 250 }
    },
    intense: {
      intensity: 0.9,
      animationSpeed: 4,
      blurAmount: 120,
      sizeRange: { min: 300, max: 500 }
    },
    dreamy: {
      intensity: 0.6,
      animationSpeed: 10,
      blurAmount: 100,
      sizeRange: { min: 200, max: 400 }
    },
    random: {
      intensity: 0.3 + Math.random() * 0.6,
      animationSpeed: 5 + Math.random() * 8,
      blurAmount: 40 + Math.random() * 80,
      sizeRange: { 
        min: 100 + Math.random() * 200, 
        max: 300 + Math.random() * 300 
      }
    }
  };
  
  const preset = presets[presetName];
  if (preset) {
    updateAuraConfig(preset);
    console.log(`🚀 应用预设: ${presetName}`);
  }
};

// 根据场景更新光圈效果
const updateAuraForScene = () => {
  const sceneIndex = storyState.value.scene_count % colorThemes.value.length;
  const newTheme = colorThemes.value[sceneIndex];
  
  // 更新当前主题索引
  currentThemeIndex.value = sceneIndex;
  
  // 随机调整强度和速度
  const newIntensity = 0.4 + Math.random() * 0.4; // 0.4-0.8
  const newSpeed = 6 + Math.random() * 4; // 6-10秒
  
  updateAuraConfig({
    colors: newTheme.colors,
    intensity: newIntensity,
    animationSpeed: newSpeed
  });
  
  console.log(`🌟 光圈效果已更新 - 场景 ${storyState.value.scene_count}, 主题: ${newTheme.name}`);
};

// 角色图片相关 - 使用动态导入
const characterImages = ref([]);

// 动态加载角色图片
const loadCharacterImages = () => {
  const images = [];
  for (let i = 1; i <= 14; i++) {
    try {
      const imageUrl = new URL(`../assets/character/${i}.png`, import.meta.url).href;
      images.push(imageUrl);
    } catch (error) {
      console.warn(`无法加载角色图片 ${i}.png:`, error);
    }
  }
  characterImages.value = images;
  console.log("🎭 已加载角色图片列表:", characterImages.value);
};

const currentCharacterImage = ref('');

// 随机选择角色图片 (避免连续选择同一个角色)
const getRandomCharacter = () => {
  if (characterImages.value.length === 0) {
    console.warn("🎭 角色图片列表为空，无法选择角色");
    return '';
  }
  
  // 如果只有一个角色图片，直接返回
  if (characterImages.value.length === 1) {
    return characterImages.value[0];
  }
  
  // 避免选择当前正在显示的角色
  let availableImages = characterImages.value.filter(img => img !== currentCharacterImage.value);
  
  // 如果所有图片都被过滤掉了（理论上不应该发生），则使用所有图片
  if (availableImages.length === 0) {
    availableImages = characterImages.value;
  }
  
  const randomIndex = Math.floor(Math.random() * availableImages.length);
  return availableImages[randomIndex];
};

// 切换角色图片
const changeCharacter = () => {
  const newCharacter = getRandomCharacter();
  if (newCharacter) {
    currentCharacterImage.value = newCharacter;
    console.log("🎭 切换角色图片:", currentCharacterImage.value);
  }
};

const storyState = ref({
  scene_count: 0,
  story_active: true, // 始终保持为 true
});

const messages = ref([]);

// 计算最新的AI消息
const latestAiMessage = computed(() => {
  const aiMessages = messages.value.filter((m) => m.role === "ai");
  return aiMessages.length > 0 ? aiMessages[aiMessages.length - 1] : null;
});

// 切换对话历史显示
const toggleChatHistory = () => {
  showChatHistory.value = !showChatHistory.value;
};

// 格式化时间
const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

// 生成更深沉复古的颜色
const getVintageColor = () => {
  const vintageColors = [
    "#8B4513",
    "#A0522D",
    "#CD853F",
    "#D2B48C",
    "#DEB887", // 棕色系
    "#556B2F",
    "#6B8E23",
    "#9ACD32",
    "#32CD32",
    "#228B22", // 深绿系
    "#191970",
    "#000080",
    "#0000CD",
    "#4169E1",
    "#1E90FF", // 深蓝系
    "#8B0000",
    "#B22222",
    "#DC143C",
    "#FF0000",
    "#FF6347", // 深红系
    "#4B0082",
    "#483D8B",
    "#6A5ACD",
    "#7B68EE",
    "#9370DB", // 紫色系
    "#B8860B",
    "#DAA520",
    "#FF8C00",
    "#FF7F50",
    "#CD5C5C", // 金黄系
    "#2F4F4F",
    "#708090",
    "#778899",
    "#696969",
    "#808080", // 灰色系
    "#8B4513",
    "#A0522D",
    "#D2691E",
    "#FF4500",
    "#FF6347", // 橙棕系
  ];
  return {
    backgroundColor:
      vintageColors[Math.floor(Math.random() * vintageColors.length)],
  };
};

// 处理发送消息
const handleSend = async () => {
  const userMessage = input.value;
  
  if (!userMessage.trim() || loading.value) return;

  // 添加用户消息到历史
  messages.value.push({ 
    role: "user", 
    text: userMessage,
    timestamp: new Date()
  });
  
  // 清空输入框
  input.value = "";
  
  loading.value = true;

  try {
    console.log("🚀 发送消息到后端:", userMessage);
    
    const response = await fetch("http://localhost:5001/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userMessage,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("🔍 完整API响应数据:", data);

    if (data.status === "success") {
      // 添加AI回复到历史
      messages.value.push({ 
        role: "ai", 
        text: data.reply,
        timestamp: new Date()
      });

      // 更新故事状态（始终保持活跃）
      if (data.scene_count !== undefined) {
        const oldSceneCount = storyState.value.scene_count;
        storyState.value.scene_count = data.scene_count;
        
        // 如果场景发生变化，切换角色图片并更新光圈效果
        if (oldSceneCount !== data.scene_count) {
          changeCharacter();
          updateAuraForScene();
        }
              } else {
          // 如果API没有返回scene_count，手动递增
          storyState.value.scene_count += 1;
          // 场景变化，切换角色图片并更新光圈效果
          changeCharacter();
          updateAuraForScene();
        }
      
      // 强制保持故事活跃状态（无限流游戏）
      storyState.value.story_active = true;

      // 如果有图片URL，发射背景更新事件
      if (data.image_url) {
        console.log("🎨 发现图片URL:", data.image_url);
        emit("backgroundUpdate", data.image_url);
        console.log("📤 已发射backgroundUpdate事件");
      } else {
        console.log("⚠️ API响应中没有image_url字段");
      }

      // 移除故事结束的检查逻辑，因为这是无限流游戏
      
    } else {
      messages.value.push({
        role: "ai",
        text: "抱歉，出现了一些问题：" + (data.error || "未知错误"),
        timestamp: new Date()
      });
    }
  } catch (error) {
    console.error("❌ 请求错误:", error);
    messages.value.push({
      role: "ai",
      text: "抱歉，连接服务器失败，请检查后端服务是否正常运行。错误详情: " + error.message,
      timestamp: new Date()
    });
  } finally {
    loading.value = false;
  }
};

// 获取初始消息的函数
const fetchInitialMessage = async () => {
  loading.value = true;
  
  try {
    console.log("🚀 获取初始消息...");
    
    const response = await fetch("http://localhost:5001/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "开始故事", // 发送一个初始化消息
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("🔍 初始消息API响应:", data);

    if (data.status === "success") {
      // 添加AI初始消息
      messages.value.push({ 
        role: "ai", 
        text: data.reply,
        timestamp: new Date()
      });

      // 更新故事状态（始终保持活跃）
      if (data.scene_count !== undefined) {
        storyState.value.scene_count = data.scene_count;
      } else {
        // 初始化时设置为1
        storyState.value.scene_count = 1;
      }
      
      // 强制保持故事活跃状态（无限流游戏）
      storyState.value.story_active = true;

      // 初始消息时也切换角色
      if (!currentCharacterImage.value) {
        changeCharacter();
      }

      // 如果有图片URL，发射背景更新事件
      if (data.image_url) {
        console.log("🎨 发现初始图片URL:", data.image_url);
        emit("backgroundUpdate", data.image_url);
      }
    } else {
      // 如果API调用失败，显示默认消息并确保故事状态正常
      messages.value.push({
        role: "ai",
        text: "欢迎来到无限的故事世界，让我们开始这段永不结束的奇妙旅程吧！",
        timestamp: new Date()
      });
      // 确保故事状态为活跃
      storyState.value.story_active = true;
      storyState.value.scene_count = 1;
    }
  } catch (error) {
    console.error("❌ 获取初始消息失败:", error);
    // 如果网络错误，显示默认消息并确保故事状态正常
    messages.value.push({
      role: "ai",
      text: "欢迎来到无限的故事世界，让我们开始这段永不结束的奇妙旅程吧！",
      timestamp: new Date()
    });
    // 确保故事状态为活跃
    storyState.value.story_active = true;
    storyState.value.scene_count = 1;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  console.log("✅ AIChat 组件已挂载 - 无限流游戏模式");
  console.log("🔗 后端API地址: http://localhost:5001/api/chat");
  
  // 强制确保初始状态正确（无限流模式）
  storyState.value.story_active = true;
  storyState.value.scene_count = 0;
  console.log("🔧 设置无限流模式初始状态:", storyState.value);
  
  // 加载角色图片
  loadCharacterImages();
  
  // 初始化角色图片
  changeCharacter();
  
  // 初始化光圈效果
  updateAuraForScene();
  
  // 获取初始消息
  fetchInitialMessage();
});

// 添加监视器来调试状态变化
watch(() => storyState.value.story_active, (newVal, oldVal) => {
  console.log("📈 story_active 状态变化:", oldVal, "->", newVal);
});

watch(() => storyState.value.scene_count, (newVal, oldVal) => {
  console.log("📈 scene_count 状态变化:", oldVal, "->", newVal);
});
</script>

<style scoped>
.chat-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  z-index: 10;
}

/* 动态模糊光圈 */
.dream-aura {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1; /* 在背景之上，其他元素之下 */
  pointer-events: none; /* 允许点击穿透 */
  overflow: hidden;
}

.dream-aura::before,
.dream-aura::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(var(--aura-blur, 80px));
  opacity: var(--aura-intensity, 0.6);
  animation: dreamFloat var(--aura-speed, 8s) infinite ease-in-out;
}

/* 左上角光圈 */
.dream-aura::before {
  top: -20%;
  left: -20%;
  width: var(--aura-size-max, 400px);
  height: var(--aura-size-max, 400px);
  background: radial-gradient(
    circle,
    var(--aura-color-1, rgba(138, 43, 226, 0.3)) 0%,
    var(--aura-color-2, rgba(75, 0, 130, 0.25)) 30%,
    transparent 70%
  );
  animation-delay: 0s;
}

/* 右下角光圈 */
.dream-aura::after {
  bottom: -20%;
  right: -20%;
  width: var(--aura-size-min, 300px);
  height: var(--aura-size-min, 300px);
  background: radial-gradient(
    circle,
    var(--aura-color-3, rgba(72, 61, 139, 0.3)) 0%,
    var(--aura-color-4, rgba(147, 112, 219, 0.25)) 30%,
    transparent 70%
  );
  animation-delay: calc(var(--aura-speed, 8s) * -0.5);
}

/* 额外的动态光点 */
.dream-aura {
  background: 
    radial-gradient(
      circle at 80% 20%,
      var(--aura-color-5, rgba(123, 104, 238, 0.2)) 0%,
      transparent 40%
    ),
    radial-gradient(
      circle at 20% 80%,
      var(--aura-color-2, rgba(75, 0, 130, 0.15)) 0%,
      transparent 40%
    ),
    radial-gradient(
      circle at 90% 90%,
      var(--aura-color-1, rgba(138, 43, 226, 0.1)) 0%,
      transparent 30%
    ),
    radial-gradient(
      circle at 10% 10%,
      var(--aura-color-4, rgba(147, 112, 219, 0.1)) 0%,
      transparent 30%
    );
  animation: dreamAura calc(var(--aura-speed, 8s) * 1.5) infinite ease-in-out;
}

/* 光圈浮动动画 */
@keyframes dreamFloat {
  0%, 100% {
    transform: scale(1) rotate(0deg) translate(0, 0);
    opacity: var(--aura-intensity, 0.6);
  }
  25% {
    transform: scale(1.2) rotate(90deg) translate(20px, -20px);
    opacity: calc(var(--aura-intensity, 0.6) * 0.8);
  }
  50% {
    transform: scale(0.8) rotate(180deg) translate(-10px, 30px);
    opacity: calc(var(--aura-intensity, 0.6) * 1.2);
  }
  75% {
    transform: scale(1.1) rotate(270deg) translate(-30px, -10px);
    opacity: calc(var(--aura-intensity, 0.6) * 0.9);
  }
}

/* 整体光圈呼吸动画 */
@keyframes dreamAura {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  33% {
    opacity: 1.2;
    transform: scale(1.05);
  }
  66% {
    opacity: 0.6;
    transform: scale(0.95);
  }
}

/* 响应式光圈 */
@media (max-width: 768px) {
  .dream-aura::before,
  .dream-aura::after {
    filter: blur(calc(var(--aura-blur, 80px) * 0.7));
  }
  
  .dream-aura::before {
    width: calc(var(--aura-size-max, 400px) * 0.7);
    height: calc(var(--aura-size-max, 400px) * 0.7);
  }
  
  .dream-aura::after {
    width: calc(var(--aura-size-min, 300px) * 0.7);
    height: calc(var(--aura-size-min, 300px) * 0.7);
  }
}

/* 角色图片层 */
.character-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 5; /* 确保在背景图之上，聊天框之下 */
  display: flex;
  justify-content: flex-end; /* 角色位于右侧 */
  align-items: flex-end; /* 角色位于底部 */
  pointer-events: none; /* 允许点击穿透到背景和聊天框 */
  padding: 20px; /* 添加一些边距 */
}

.character-image {
  max-width: 2000px; /* 固定最大宽度，调大 */
  max-height: 70vh; /* 最大高度为视口的70%，调大 */
  object-fit: contain;
  opacity: 0.4; /* 适中的透明度，既能看到又不会干扰聊天 */
  filter: blur(0.5px) brightness(0.8); /* 轻微模糊和变暗，营造背景感 */
  transform: translateX(10px); /* 稍微向右偏移 */
  transition: all 1.2s ease-in-out; /* 添加平滑过渡动画 */
  border-radius: 10px; /* 添加圆角 */
}

/* 角色切换动画 */
@keyframes characterFadeIn {
  0% {
    opacity: 0;
    transform: translateX(30px) scale(0.9);
  }
  100% {
    opacity: 0.4;
    transform: translateX(10px) scale(1);
  }
}

.character-image {
  animation: characterFadeIn 1.2s ease-out;
}

/* 响应式角色图片 */
@media (max-width: 768px) {
  .character-layer {
    justify-content: center; /* 在小屏幕上居中 */
    align-items: center;
    padding: 10px;
  }
  
  .character-image {
    max-width: 200px;
    max-height: 40vh;
    opacity: 0.25; /* 在小屏幕上更透明 */
    transform: translateX(0); /* 移除偏移 */
  }
}

/* 对话历史样式 */
.chat-history {
  position: fixed;
  top: 80px;
  left: 20px;
  right: 20px;
  bottom: 100px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 20;
  overflow: hidden;
}

.chat-messages {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.message-wrapper {
  margin-bottom: 15px;
  display: flex;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.ai {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.message-wrapper.user .message-bubble {
  background: linear-gradient(135deg, #007AFF, #5856D6);
  color: white;
}

.message-wrapper.ai .message-bubble {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
}

.message-text {
  margin: 0 0 4px 0;
  line-height: 1.4;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
}

/* 聊天控制按钮 */
.chat-controls {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 25;
}

.chat-toggle-btn {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.chat-toggle-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.05);
}

.chat-toggle-btn.active {
  background: rgba(0, 122, 255, 0.8);
}

/* 故事状态样式 */
.story-status {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  padding: 10px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  backdrop-filter: blur(10px);
  z-index: 15;
  min-width: 200px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

.status-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.scene-count {
  color: #ffd700;
  font-size: 14px;
  font-weight: bold;
}

.story-state {
  color: #4caf50;
  font-size: 12px;
  font-weight: bold;
}

.story-state.story-ended {
  color: #ff6b6b;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(to right, #ffd700, #ffa500);
  border-radius: 2px;
  transition: width 0.3s ease-in-out;
}

/* AI对话框样式 (透明设计) */
.ai-dialog-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

/* Loading组件包装器 */
.loading-wrapper {
  position: fixed;
  bottom: 140px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  z-index: 10;
  background: rgba(20, 20, 30, 0.8);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.ai-dialog {
  background: rgba(20, 20, 30, 0.7);
  border-radius: 12px;
  min-width: 400px;
  max-width: 600px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.ai-dialog-header {
  background: rgba(10, 10, 20, 0.6);
  padding: 12px 20px;
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-dialog-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 2px;
}

.ai-dialog-content {
  padding: 20px;
}

.ai-response {
  color: #ffffff;
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
  text-align: center;
}



/* 简易输入框样式 */
.simple-input-container {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 600px;
  z-index: 15;
}

.input-wrapper {
  background: rgba(20, 20, 30, 0.7);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 15px;
  align-items: center;
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.story-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  padding: 15px;
  outline: none;
  color: #ffffff;
  placeholder-color: #aaa;
}

.story-input::placeholder {
  color: #aaa;
}

.send-button {
  background: linear-gradient(135deg, #007AFF, #5856D6);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 15px 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.4);
}

.send-button:disabled {
  background: rgba(100, 100, 100, 0.5);
  cursor: not-allowed;
  transform: none;
}

/* 光圈控制按钮 */
.aura-controls {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 25;
}

.aura-control-btn {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.aura-control-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
}

.aura-control-btn.active {
  background: rgba(138, 43, 226, 0.8);
  border-color: rgba(138, 43, 226, 0.5);
}

/* 光圈调节面板 */
.aura-panel {
  position: fixed;
  top: 80px;
  right: 20px;
  width: 320px;
  max-height: 80vh;
  background: rgba(20, 20, 30, 0.95);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
  z-index: 30;
  overflow: hidden;
  animation: panelSlideIn 0.3s ease-out;
}

@keyframes panelSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.aura-panel-header {
  background: rgba(10, 10, 20, 0.8);
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.aura-panel-header h3 {
  color: #ffffff;
  margin: 0;
  font-size: 16px;
  font-weight: bold;
}

.close-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.aura-panel-content {
  padding: 20px;
  max-height: calc(80vh - 80px);
  overflow-y: auto;
}

.control-group {
  margin-bottom: 20px;
}

.control-group label {
  display: block;
  color: #ffffff;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}

.slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.2);
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8A2BE2, #4B0082);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(138, 43, 226, 0.4);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8A2BE2, #4B0082);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 8px rgba(138, 43, 226, 0.4);
}

/* 主题按钮 */
.theme-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 8px;
}

.theme-btn {
  padding: 12px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.3s ease;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.theme-btn:hover {
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.4);
}

.theme-btn.active {
  border-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 16px rgba(255, 255, 255, 0.3);
}

/* 预设按钮 */
.preset-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 8px;
}

.preset-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.preset-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-dialog {
    min-width: 300px;
    max-width: 90vw;
  }

  .simple-input-container {
    width: 95%;
    bottom: 15px;
  }

  .input-wrapper {
    padding: 15px;
  }

  .story-input {
    font-size: 14px;
    padding: 12px;
  }

  .send-button {
    font-size: 14px;
    padding: 10px 20px;
    min-width: 100px;
  }

  .chat-history {
    top: 60px;
    left: 10px;
    right: 10px;
    bottom: 80px;
  }

  .aura-controls {
    top: 15px;
    right: 15px;
  }

  .aura-control-btn {
    padding: 10px 18px;
    font-size: 13px;
  }

  .aura-panel {
    right: 10px;
    left: 10px;
    width: auto;
    top: 70px;
  }

  .theme-buttons,
  .preset-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
