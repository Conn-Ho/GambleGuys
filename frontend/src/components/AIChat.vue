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

    <!-- EEG情绪状态显示 -->
    <!-- <div class="emotion-status" v-if="emotionListening || latestEmotionData">
      <div class="emotion-indicator" :class="{ active: emotionListening }">
        <div class="emotion-icon">🧠</div>
        <div class="emotion-info">
          <div class="emotion-state">
            {{ emotionListening ? "EEG监听中" : "EEG已停止" }}
          </div>
          <div class="emotion-data" v-if="latestEmotionData">
            <span class="current-emotion">{{ latestEmotionData.emotion }}</span>
            <span class="emotion-intensity">{{ (latestEmotionData.intensity * 100).toFixed(0) }}%</span>
          </div>
          <div class="emotion-history" v-if="emotionHistory.length > 0">
            <span class="history-label">历史: </span>
            <span class="history-count">{{ emotionHistory.length }}/{{ maxHistoryLength }}</span>
          </div>
          <div class="emotion-mapping" v-if="latestEmotionData">
            <span class="mapping-label">光圈: </span>
            <span class="mapping-status active">已映射</span>
          </div>
        </div>
      </div>
    </div> -->

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
      v-if="(latestAiMessage || loading) && !showChatHistory"
      class="ai-dialog-wrapper"
      style="position: fixed; bottom: 140px; left: 50%; transform: translateX(-50%); display: flex; justify-content: center; pointer-events: none; z-index: 10;"
    >
      <div class="ai-dialog" style="pointer-events: auto;">
        <div class="ai-dialog-content">
          <p class="ai-response" v-if="!loading">{{ latestAiMessage.text }}</p>
          <p class="ai-response loading-dots" v-if="loading">
            <span class="dot">.</span>
            <span class="dot">.</span>
            <span class="dot">.</span>
          </p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <!-- <div v-if="loading" class="loading-wrapper">
      <Loading :inline="true" text="正在思考..." />
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
import { ref, nextTick, onMounted, computed, watch, onUnmounted } from "vue";
import Loading from './Loading.vue';

// 定义发射事件
const emit = defineEmits(["backgroundUpdate"]);

const input = ref("");
const loading = ref(false);
const showChatHistory = ref(false);
const showAuraPanel = ref(false);
const currentThemeIndex = ref(0);

// EEG情绪监听相关
const emotionListening = ref(false);
const latestEmotionData = ref(null);
const emotionWebSocket = ref(null);
const showEmotionTest = ref(false);

// 情绪历史跟踪（用于平滑过渡）
const emotionHistory = ref([]);
const maxHistoryLength = 5; // 保留最近5次情绪数据

// 情绪到光圈效果的映射配置
const emotionAuraMapping = {
  // 积极情绪组
  "Happy (开心)": {
    colors: [
      'rgba(255, 215, 0, 0.4)',    // 金黄
      'rgba(255, 165, 0, 0.35)',   // 橙色
      'rgba(255, 140, 0, 0.4)',    // 深橙
      'rgba(255, 193, 7, 0.35)',   // 琥珀色
      'rgba(255, 235, 59, 0.3)'    // 亮黄
    ],
    baseIntensity: 0.7,
    baseSpeed: 6,
    baseBlur: 70,
    sizeRange: { min: 250, max: 450 }
  },
  
  "Excited (激动)": {
    colors: [
      'rgba(255, 87, 34, 0.5)',    // 橙红
      'rgba(244, 67, 54, 0.45)',   // 红色
      'rgba(255, 152, 0, 0.4)',    // 橙色
      'rgba(255, 193, 7, 0.35)',   // 琥珀
      'rgba(255, 235, 59, 0.4)'    // 黄色
    ],
    baseIntensity: 0.9,
    baseSpeed: 3,
    baseBlur: 90,
    sizeRange: { min: 300, max: 600 }
  },
  
  "Surprised (惊喜)": {
    colors: [
      'rgba(156, 39, 176, 0.4)',   // 紫色
      'rgba(103, 58, 183, 0.35)',  // 深紫
      'rgba(63, 81, 181, 0.4)',    // 靛蓝
      'rgba(33, 150, 243, 0.35)',  // 蓝色
      'rgba(0, 188, 212, 0.3)'     // 青色
    ],
    baseIntensity: 0.8,
    baseSpeed: 2,
    baseBlur: 100,
    sizeRange: { min: 200, max: 500 }
  },
  
  "Relaxed (放松)": {
    colors: [
      'rgba(76, 175, 80, 0.3)',    // 绿色
      'rgba(139, 195, 74, 0.25)',  // 浅绿
      'rgba(156, 204, 101, 0.3)',  // 淡绿
      'rgba(174, 213, 129, 0.25)', // 更淡绿
      'rgba(200, 230, 201, 0.2)'   // 极淡绿
    ],
    baseIntensity: 0.4,
    baseSpeed: 12,
    baseBlur: 50,
    sizeRange: { min: 180, max: 280 }
  },
  
  "Pleased (平静)": {
    colors: [
      'rgba(96, 125, 139, 0.3)',   // 蓝灰
      'rgba(120, 144, 156, 0.25)', // 浅蓝灰
      'rgba(144, 164, 174, 0.3)',  // 更浅蓝灰
      'rgba(176, 190, 197, 0.25)', // 淡蓝灰
      'rgba(207, 216, 220, 0.2)'   // 极淡蓝灰
    ],
    baseIntensity: 0.35,
    baseSpeed: 10,
    baseBlur: 60,
    sizeRange: { min: 200, max: 350 }
  },
  
  // 消极情绪组
  "Sad (悲伤)": {
    colors: [
      'rgba(63, 81, 181, 0.35)',   // 深蓝
      'rgba(48, 63, 159, 0.3)',    // 更深蓝
      'rgba(40, 53, 147, 0.35)',   // 极深蓝
      'rgba(26, 35, 126, 0.3)',    // 靛蓝
      'rgba(13, 18, 87, 0.25)'     // 深靛蓝
    ],
    baseIntensity: 0.4,
    baseSpeed: 15,
    baseBlur: 80,
    sizeRange: { min: 150, max: 300 }
  },
  
  "Angry (愤怒)": {
    colors: [
      'rgba(244, 67, 54, 0.6)',    // 红色
      'rgba(229, 57, 53, 0.55)',   // 深红
      'rgba(211, 47, 47, 0.5)',    // 更深红
      'rgba(198, 40, 40, 0.45)',   // 暗红
      'rgba(183, 28, 28, 0.4)'     // 极深红
    ],
    baseIntensity: 1.0,
    baseSpeed: 2,
    baseBlur: 120,
    sizeRange: { min: 350, max: 700 }
  },
  
  "Fear (恐惧)": {
    colors: [
      'rgba(69, 39, 160, 0.4)',    // 深紫
      'rgba(49, 27, 146, 0.35)',   // 更深紫
      'rgba(26, 13, 132, 0.4)',    // 极深紫
      'rgba(17, 8, 89, 0.35)',     // 黑紫
      'rgba(8, 3, 45, 0.3)'        // 极黑紫
    ],
    baseIntensity: 0.7,
    baseSpeed: 4,
    baseBlur: 150,
    sizeRange: { min: 200, max: 400 }
  },
  
  "Depressed (沮丧)": {
    colors: [
      'rgba(55, 71, 79, 0.3)',     // 深灰蓝
      'rgba(38, 50, 56, 0.25)',    // 更深灰蓝
      'rgba(33, 43, 49, 0.3)',     // 极深灰
      'rgba(23, 31, 35, 0.25)',    // 黑灰
      'rgba(13, 18, 20, 0.2)'      // 极黑
    ],
    baseIntensity: 0.25,
    baseSpeed: 20,
    baseBlur: 40,
    sizeRange: { min: 100, max: 200 }
  },
  
  "Tired (疲倦)": {
    colors: [
      'rgba(121, 85, 72, 0.3)',    // 棕色
      'rgba(93, 64, 55, 0.25)',    // 深棕
      'rgba(78, 52, 46, 0.3)',     // 更深棕
      'rgba(62, 39, 35, 0.25)',    // 暗棕
      'rgba(40, 26, 23, 0.2)'      // 极深棕
    ],
    baseIntensity: 0.3,
    baseSpeed: 18,
    baseBlur: 45,
    sizeRange: { min: 120, max: 250 }
  },
  
  "Sleepy (困倦)": {
    colors: [
      'rgba(94, 106, 142, 0.25)',  // 紫灰
      'rgba(81, 91, 122, 0.2)',    // 深紫灰
      'rgba(69, 77, 102, 0.25)',   // 更深紫灰
      'rgba(56, 62, 81, 0.2)',     // 暗紫灰
      'rgba(43, 47, 61, 0.15)'     // 极暗紫灰
    ],
    baseIntensity: 0.2,
    baseSpeed: 25,
    baseBlur: 35,
    sizeRange: { min: 100, max: 180 }
  },
  
  // 中性和其他情绪
  "Neutral (中性)": {
    colors: [
      'rgba(138, 43, 226, 0.3)',   // 默认紫色
      'rgba(75, 0, 130, 0.25)',
      'rgba(72, 61, 139, 0.3)',
      'rgba(147, 112, 219, 0.25)',
      'rgba(123, 104, 238, 0.3)'
    ],
    baseIntensity: 0.5,
    baseSpeed: 8,
    baseBlur: 80,
    sizeRange: { min: 200, max: 400 }
  },
  
  "Bored (无聊)": {
    colors: [
      'rgba(158, 158, 158, 0.25)', // 灰色
      'rgba(117, 117, 117, 0.2)',  // 深灰
      'rgba(97, 97, 97, 0.25)',    // 更深灰
      'rgba(76, 76, 76, 0.2)',     // 暗灰
      'rgba(55, 55, 55, 0.15)'     // 极深灰
    ],
    baseIntensity: 0.2,
    baseSpeed: 30,
    baseBlur: 30,
    sizeRange: { min: 150, max: 250 }
  },
  
  "Contempt (轻蔑)": {
    colors: [
      'rgba(136, 14, 79, 0.4)',    // 深洋红
      'rgba(106, 11, 61, 0.35)',   // 更深洋红
      'rgba(74, 8, 43, 0.4)',      // 暗洋红
      'rgba(56, 6, 32, 0.35)',     // 极深洋红
      'rgba(38, 4, 21, 0.3)'       // 黑洋红
    ],
    baseIntensity: 0.6,
    baseSpeed: 6,
    baseBlur: 100,
    sizeRange: { min: 180, max: 380 }
  },
  
  "Disgust (厌恶)": {
    colors: [
      'rgba(129, 119, 23, 0.4)',   // 深黄绿
      'rgba(100, 92, 18, 0.35)',   // 暗黄绿
      'rgba(71, 65, 13, 0.4)',     // 更深黄绿
      'rgba(51, 46, 9, 0.35)',     // 极深黄绿
      'rgba(31, 28, 5, 0.3)'       // 黑黄绿
    ],
    baseIntensity: 0.5,
    baseSpeed: 5,
    baseBlur: 110,
    sizeRange: { min: 160, max: 320 }
  },
  
  "Miserable (痛苦)": {
    colors: [
      'rgba(136, 14, 14, 0.5)',    // 深红
      'rgba(101, 10, 10, 0.45)',   // 暗红
      'rgba(66, 7, 7, 0.5)',       // 更深红
      'rgba(46, 5, 5, 0.45)',      // 极深红
      'rgba(26, 3, 3, 0.4)'        // 黑红
    ],
    baseIntensity: 0.8,
    baseSpeed: 7,
    baseBlur: 130,
    sizeRange: { min: 220, max: 480 }
  }
};

// 启动情绪监听
const startEmotionListening = () => {
  if (emotionListening.value) return;
  
  try {
    // 尝试连接EEG音频服务的WebSocket (如果有的话)
    // 或者使用HTTP轮询方式
    emotionListening.value = true;
    console.log("🧠 开始监听EEG情绪数据...");
    
    // 使用HTTP轮询方式获取情绪数据
    startEmotionPolling();
    
  } catch (error) {
    console.error("❌ 启动情绪监听失败:", error);
    emotionListening.value = false;
  }
};

// HTTP轮询获取情绪数据
const startEmotionPolling = () => {
  const pollInterval = 1500; // 1.5秒轮询一次，更频繁的更新
  
  const poll = async () => {
    if (!emotionListening.value) return;
    
    try {
      // 从音频服务获取当前情绪状态
      const response = await fetch("http://localhost:8080/status");
      if (response.ok) {
        const data = await response.json();
        
        // 检查是否有prompt_status包含当前情绪
        if (data.prompt_status && data.prompt_status.current_emotion && data.prompt_status.current_intensity !== undefined) {
          const emotion = data.prompt_status.current_emotion;
          const intensity = data.prompt_status.current_intensity;
          
          // 检查是否是新的情绪数据（避免重复应用相同的情绪）
          const isNewEmotion = !latestEmotionData.value || 
                              latestEmotionData.value.emotion !== emotion ||
                              Math.abs(latestEmotionData.value.intensity - intensity) > 0.05; // 降低阈值，更敏感
          
          // 更新情绪历史
          if (isNewEmotion) {
            emotionHistory.value.push({
              emotion: emotion,
              intensity: intensity,
              timestamp: Date.now()
            });
            
            // 保持历史长度限制
            if (emotionHistory.value.length > maxHistoryLength) {
              emotionHistory.value.shift();
            }
          }
          
          // 更新最新情绪数据
          latestEmotionData.value = {
            emotion: emotion,
            intensity: intensity,
            timestamp: Date.now()
          };
          
          // 只在情绪有显著变化时应用到光圈效果
          if (isNewEmotion) {
            console.log(`🧠 检测到新情绪: ${emotion} (强度: ${(intensity * 100).toFixed(1)}%)`);
            applySmoothedEmotionToAura(emotion, intensity);
          }
        }
      }
    } catch (error) {
      // 静默处理连接错误，避免日志垃圾
      if (emotionListening.value) {
        console.warn("⚠️ 情绪数据轮询失败:", error.message);
      }
    }
    
    // 继续轮询
    if (emotionListening.value) {
      setTimeout(poll, pollInterval);
    }
  };
  
  poll();
};

// 停止情绪监听
const stopEmotionListening = () => {
  emotionListening.value = false;
  if (emotionWebSocket.value) {
    emotionWebSocket.value.close();
    emotionWebSocket.value = null;
  }
  console.log("🛑 已停止情绪监听");
};

// 带历史平滑的情绪应用函数
const applySmoothedEmotionToAura = (emotion, intensity) => {
  // 如果有历史数据，计算平滑后的强度
  let smoothedIntensity = intensity;
  
  if (emotionHistory.value.length > 1) {
    // 计算最近几次相同情绪的平均强度
    const recentSameEmotions = emotionHistory.value.filter(h => h.emotion === emotion);
    if (recentSameEmotions.length > 1) {
      const totalIntensity = recentSameEmotions.reduce((sum, h) => sum + h.intensity, 0);
      const avgIntensity = totalIntensity / recentSameEmotions.length;
      
      // 使用加权平均：70%当前值 + 30%历史平均
      smoothedIntensity = intensity * 0.7 + avgIntensity * 0.3;
      
      console.log(`📊 情绪强度平滑: ${emotion} | 原始: ${(intensity * 100).toFixed(1)}% | 平滑: ${(smoothedIntensity * 100).toFixed(1)}%`);
    }
  }
  
  // 应用平滑后的情绪到光圈
  applyEmotionToAura(emotion, smoothedIntensity);
};

// 应用情绪到光圈效果
const applyEmotionToAura = (emotion, intensity) => {
  // 获取情绪映射配置，支持模糊匹配
  let emotionConfig = emotionAuraMapping[emotion];
  
  // 如果找不到精确匹配，尝试部分匹配
  if (!emotionConfig) {
    const emotionLower = emotion.toLowerCase();
    const matchingKey = Object.keys(emotionAuraMapping).find(key => 
      key.toLowerCase().includes(emotionLower) || 
      emotionLower.includes(key.toLowerCase().split(' ')[0])
    );
    emotionConfig = matchingKey ? emotionAuraMapping[matchingKey] : emotionAuraMapping["Neutral (中性)"];
    
    if (matchingKey) {
      console.log(`🎯 情绪模糊匹配: ${emotion} -> ${matchingKey}`);
    } else {
      console.log(`⚠️ 未知情绪，使用默认配置: ${emotion}`);
    }
  }
  
  // 计算强度调节系数 (intensity范围通常是0-1)
  const intensityFactor = Math.max(0.1, Math.min(1.0, intensity));
  
  // 平滑强度调节曲线
  const smoothIntensity = Math.sin(intensityFactor * Math.PI / 2); // 使用正弦函数平滑过渡
  
  // 应用强度调节
  const adjustedIntensity = emotionConfig.baseIntensity * (0.5 + smoothIntensity * 0.5);
  const adjustedSpeed = emotionConfig.baseSpeed / Math.max(0.3, intensityFactor); // 强度越高速度越快
  const adjustedBlur = emotionConfig.baseBlur * (0.6 + smoothIntensity * 0.4); // 强度影响模糊度
  
  // 尺寸范围根据强度调整，使用更平滑的缩放
  const sizeMultiplier = 0.8 + smoothIntensity * 0.4; // 0.8到1.2的范围
  const adjustedSizeRange = {
    min: Math.floor(emotionConfig.sizeRange.min * sizeMultiplier),
    max: Math.floor(emotionConfig.sizeRange.max * sizeMultiplier)
  };
  
  // 添加颜色强度调节
  const enhancedColors = emotionConfig.colors.map(color => {
    // 根据强度调节颜色透明度
    const rgba = color.match(/rgba?\(([^)]+)\)/)[1].split(',');
    const [r, g, b] = rgba.slice(0, 3).map(c => c.trim());
    const baseAlpha = parseFloat(rgba[3] || '1');
    const adjustedAlpha = Math.min(1, baseAlpha * (0.7 + smoothIntensity * 0.6));
    return `rgba(${r}, ${g}, ${b}, ${adjustedAlpha.toFixed(3)})`;
  });
  
  // 更新光圈配置
  updateAuraConfig({
    colors: enhancedColors,
    intensity: adjustedIntensity,
    animationSpeed: adjustedSpeed,
    blurAmount: adjustedBlur,
    sizeRange: adjustedSizeRange
  });
  
  console.log(`🌟 情绪光圈映射: ${emotion} | 原始强度: ${(intensity * 100).toFixed(1)}% | 平滑强度: ${(smoothIntensity * 100).toFixed(1)}% | 光圈强度: ${adjustedIntensity.toFixed(2)}`);
};

// 手动测试情绪效果
const testEmotionEffect = (emotion) => {
  const testIntensity = 0.8; // 测试用强度
  applyEmotionToAura(emotion, testIntensity);
  console.log(`🧪 测试情绪效果: ${emotion}`);
};

// 获取情绪的主要类别（用于相似情绪的渐变处理）
const getEmotionCategory = (emotion) => {
  const emotionLower = emotion.toLowerCase();
  
  if (emotionLower.includes('happy') || emotionLower.includes('excited') || emotionLower.includes('pleased')) {
    return 'positive';
  } else if (emotionLower.includes('sad') || emotionLower.includes('depressed') || emotionLower.includes('miserable')) {
    return 'negative';
  } else if (emotionLower.includes('angry') || emotionLower.includes('fear') || emotionLower.includes('disgust')) {
    return 'intense';
  } else if (emotionLower.includes('relaxed') || emotionLower.includes('sleepy') || emotionLower.includes('tired')) {
    return 'calm';
  } else {
    return 'neutral';
  }
};

// 计算情绪间的混合效果（当快速切换情绪时）
const blendEmotionEffects = (currentEmotion, previousEmotion, blendRatio = 0.3) => {
  const currentConfig = emotionAuraMapping[currentEmotion] || emotionAuraMapping["Neutral (中性)"];
  const previousConfig = emotionAuraMapping[previousEmotion] || emotionAuraMapping["Neutral (中性)"];
  
  // 混合颜色
  const blendedColors = currentConfig.colors.map((currentColor, index) => {
    const prevColor = previousConfig.colors[index] || previousConfig.colors[0];
    
    // 简单的颜色混合（这里只是示例，实际可以更复杂）
    const currentRgba = currentColor.match(/rgba?\(([^)]+)\)/)[1].split(',');
    const prevRgba = prevColor.match(/rgba?\(([^)]+)\)/)[1].split(',');
    
    const blendedR = Math.round(parseFloat(currentRgba[0]) * (1 - blendRatio) + parseFloat(prevRgba[0]) * blendRatio);
    const blendedG = Math.round(parseFloat(currentRgba[1]) * (1 - blendRatio) + parseFloat(prevRgba[1]) * blendRatio);
    const blendedB = Math.round(parseFloat(currentRgba[2]) * (1 - blendRatio) + parseFloat(prevRgba[2]) * blendRatio);
    const blendedA = (parseFloat(currentRgba[3] || '1') * (1 - blendRatio) + parseFloat(prevRgba[3] || '1') * blendRatio).toFixed(3);
    
    return `rgba(${blendedR}, ${blendedG}, ${blendedB}, ${blendedA})`;
  });
  
  return {
    ...currentConfig,
    colors: blendedColors,
    baseIntensity: currentConfig.baseIntensity * (1 - blendRatio) + previousConfig.baseIntensity * blendRatio,
    baseSpeed: currentConfig.baseSpeed * (1 - blendRatio) + previousConfig.baseSpeed * blendRatio
  };
};

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
  
  // 启动情绪监听
  startEmotionListening();
});

// 在组件卸载时停止监听
onUnmounted(() => {
  stopEmotionListening();
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
  max-height: 80vh; /* 最大高度为视口的70%，调大 */
  object-fit: contain;
  opacity: 0.9; /* 适中的透明度，既能看到又不会干扰聊天 */
  filter: blur(0.5px) brightness(0.8); /* 轻微模糊和变暗，营造背景感 */
  transform: translate(10px, 30px); /* 稍微向右并向下偏移 */
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

/* EEG情绪状态显示 */
.emotion-status {
  position: fixed;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  padding: 12px 16px;
  backdrop-filter: blur(10px);
  z-index: 15;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.emotion-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.emotion-indicator.active .emotion-icon {
  animation: brainPulse 2s infinite ease-in-out;
}

@keyframes brainPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.emotion-icon {
  font-size: 20px;
  color: #64b5f6;
}

.emotion-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.emotion-state {
  color: #ffffff;
  font-size: 12px;
  font-weight: bold;
}

.emotion-data {
  display: flex;
  gap: 8px;
  align-items: center;
}

.current-emotion {
  color: #ffeb3b;
  font-size: 11px;
  font-weight: bold;
  background: rgba(255, 235, 59, 0.2);
  padding: 2px 6px;
  border-radius: 8px;
}

.emotion-intensity {
  color: #4caf50;
  font-size: 11px;
  font-weight: bold;
}

.emotion-history {
  display: flex;
  gap: 4px;
  align-items: center;
  margin-top: 2px;
}

.history-label {
  color: #9e9e9e;
  font-size: 10px;
}

.history-count {
  color: #2196f3;
  font-size: 10px;
  font-weight: bold;
  background: rgba(33, 150, 243, 0.2);
  padding: 1px 4px;
  border-radius: 6px;
}

.emotion-mapping {
  display: flex;
  gap: 4px;
  align-items: center;
  margin-top: 2px;
}

.mapping-label {
  color: #9e9e9e;
  font-size: 10px;
}

.mapping-status {
  font-size: 10px;
  font-weight: bold;
  padding: 1px 4px;
  border-radius: 6px;
}

.mapping-status.active {
  color: #4caf50;
  background: rgba(76, 175, 80, 0.2);
  animation: mappingPulse 2s infinite ease-in-out;
}

@keyframes mappingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 情绪控制按钮 */
.emotion-controls {
  position: fixed;
  top: 80px;
  left: 20px;
  z-index: 25;
}

.emotion-control-btn {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  font-size: 13px;
  font-weight: bold;
}

.emotion-control-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.05);
}

.emotion-control-btn.active {
  background: rgba(255, 235, 59, 0.8);
  color: #000;
  border-color: rgba(255, 235, 59, 0.5);
}

/* 情绪测试面板 */
.emotion-test-panel {
  position: fixed;
  top: 140px;
  left: 20px;
  width: 280px;
  max-height: 60vh;
  background: rgba(20, 20, 30, 0.95);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
  z-index: 30;
  overflow: hidden;
  animation: panelSlideIn 0.3s ease-out;
}

.panel-header {
  background: rgba(10, 10, 20, 0.8);
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  color: #ffffff;
  margin: 0;
  font-size: 14px;
  font-weight: bold;
}

.close-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.emotion-test-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  padding: 12px 16px;
}

.emotion-test-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  padding: 8px 4px;
  cursor: pointer;
  font-size: 10px;
  font-weight: bold;
  transition: all 0.3s ease;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.emotion-test-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.4);
}

.emotion-test-btn:active {
  transform: scale(0.95);
  background: rgba(255, 235, 59, 0.3);
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

/* 加载动画样式 */
.loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-dots .dot {
  font-size: 24px;
  animation: loadingDots 1.5s infinite ease-in-out;
  opacity: 0;
}

.loading-dots .dot:nth-child(1) {
  animation-delay: 0s;
}

.loading-dots .dot:nth-child(2) {
  animation-delay: 0.3s;
}

.loading-dots .dot:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes loadingDots {
  0%, 20% {
    opacity: 0;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
  80%, 100% {
    opacity: 0;
    transform: scale(0.8);
  }
}
</style>
