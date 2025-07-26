<template>
  <div class="audio-status-monitor">
    <div class="status-card" :class="statusClass">
      <div class="status-header">
        <h3>🎵 音频生成状态</h3>
        <div class="connection-indicator" :class="{ connected: isConnected }">
          {{ isConnected ? '🟢 已连接' : '🔴 未连接' }}
        </div>
      </div>

      <div class="status-content">
        <!-- 状态显示 -->
        <div class="status-display">
          <div class="status-text">
            <span class="status-label">{{ statusIcon }} {{ audioStatus.message }}</span>
          </div>

          <!-- 缓冲进度条 -->
          <div v-if="audioStatus.status === 'buffering'" class="progress-container">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: audioStatus.buffer_progress + '%' }"
              ></div>
            </div>
            <span class="progress-text">{{ audioStatus.buffer_progress }}%</span>
          </div>

          <!-- 错误详情 -->
          <div v-if="audioStatus.error_details" class="error-details">
            <details>
              <summary>错误详情</summary>
              <pre>{{ audioStatus.error_details }}</pre>
            </details>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="status-actions">
          <button 
            v-if="audioStatus.status === 'error'" 
            @click="restartAudio"
            :disabled="isRestarting"
            class="restart-btn"
          >
            {{ isRestarting ? '重启中...' : '🔄 重启音频服务' }}
          </button>

          <button @click="refreshStatus" class="refresh-btn">
            🔄 刷新状态
          </button>
        </div>
      </div>
    </div>

    <!-- 连接日志 -->
    <div class="connection-log">
      <h4>连接日志</h4>
      <div class="log-container">
        <div v-for="(log, index) in connectionLogs" :key="index" class="log-entry">
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AudioStatusMonitor',
  data() {
    return {
      audioStatus: {
        status: 'stopped',
        message: '未知状态',
        is_playing: false,
        buffer_progress: 0,
        error_details: null,
        timestamp: 0
      },
      isConnected: false,
      isRestarting: false,
      websocket: null,
      connectionLogs: [],
      reconnectTimer: null,
      maxReconnectAttempts: 10,
      reconnectAttempts: 0
    }
  },
  computed: {
    statusClass() {
      return {
        'status-playing': this.audioStatus.status === 'playing',
        'status-buffering': this.audioStatus.status === 'buffering',
        'status-error': this.audioStatus.status === 'error',
        'status-connecting': ['connecting', 'initializing', 'starting'].includes(this.audioStatus.status),
        'status-stopped': this.audioStatus.status === 'stopped'
      }
    },
    statusIcon() {
      const icons = {
        'stopped': '⏹️',
        'starting': '🚀',
        'initializing': '⚙️',
        'connecting': '🔗',
        'connected': '✅',
        'buffering': '⏳',
        'playing': '🎵',
        'error': '❌',
        'stopping': '🛑'
      }
      return icons[this.audioStatus.status] || '❓'
    }
  },
  mounted() {
    this.initWebSocket()
    this.refreshStatus()
  },
  beforeUnmount() {
    this.closeWebSocket()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }
  },
  methods: {
    initWebSocket() {
      try {
        const wsUrl = 'ws://localhost:8080/ws/audio_status'
        this.websocket = new WebSocket(wsUrl)
        
        this.websocket.onopen = () => {
          this.isConnected = true
          this.reconnectAttempts = 0
          this.addLog('WebSocket连接已建立')
        }
        
        this.websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.audioStatus = data
            this.addLog(`状态更新: ${data.status} - ${data.message}`)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }
        
        this.websocket.onclose = () => {
          this.isConnected = false
          this.addLog('WebSocket连接已断开')
          this.scheduleReconnect()
        }
        
        this.websocket.onerror = (error) => {
          console.error('WebSocket错误:', error)
          this.addLog('WebSocket连接错误')
        }
        
      } catch (error) {
        console.error('初始化WebSocket失败:', error)
        this.addLog('初始化WebSocket失败')
      }
    },
    
    closeWebSocket() {
      if (this.websocket) {
        this.websocket.close()
        this.websocket = null
      }
    },
    
    scheduleReconnect() {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
        
        this.addLog(`${delay/1000}秒后尝试重新连接... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        
        this.reconnectTimer = setTimeout(() => {
          this.initWebSocket()
        }, delay)
      } else {
        this.addLog('达到最大重连次数，停止重连')
      }
    },
    
    async refreshStatus() {
      try {
        const response = await fetch('http://localhost:8080/audio_status')
        if (response.ok) {
          this.audioStatus = await response.json()
          this.addLog('手动刷新状态成功')
        } else {
          this.addLog('刷新状态失败: HTTP ' + response.status)
        }
      } catch (error) {
        console.error('刷新状态失败:', error)
        this.addLog('刷新状态失败: ' + error.message)
      }
    },
    
    async restartAudio() {
      this.isRestarting = true
      try {
        const response = await fetch('http://localhost:8080/restart_audio', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const result = await response.json()
          this.addLog('音频服务重启请求已发送')
        } else {
          this.addLog('重启请求失败: HTTP ' + response.status)
        }
      } catch (error) {
        console.error('重启音频服务失败:', error)
        this.addLog('重启请求失败: ' + error.message)
      } finally {
        this.isRestarting = false
      }
    },
    
    addLog(message) {
      const log = {
        timestamp: new Date(),
        message: message
      }
      this.connectionLogs.unshift(log)
      
      // 限制日志条数
      if (this.connectionLogs.length > 50) {
        this.connectionLogs = this.connectionLogs.slice(0, 50)
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.audio-status-monitor {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.status-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.status-header h3 {
  margin: 0;
  color: #495057;
}

.connection-indicator {
  padding: 4px 8px;
  border-radius: 4px;
  background: #dc3545;
  color: white;
  font-size: 12px;
  transition: background-color 0.3s ease;
}

.connection-indicator.connected {
  background: #28a745;
}

.status-content {
  padding: 20px;
}

.status-display {
  margin-bottom: 20px;
}

.status-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
}

.status-label {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 6px;
  background: #e9ecef;
  color: #495057;
}

/* 状态颜色 */
.status-playing .status-label {
  background: #d4edda;
  color: #155724;
}

.status-buffering .status-label {
  background: #fff3cd;
  color: #856404;
}

.status-error .status-label {
  background: #f8d7da;
  color: #721c24;
}

.status-connecting .status-label {
  background: #d1ecf1;
  color: #0c5460;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #007bff;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #6c757d;
  min-width: 35px;
}

.error-details {
  margin-top: 10px;
}

.error-details details {
  cursor: pointer;
}

.error-details pre {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

.status-actions {
  display: flex;
  gap: 10px;
}

.restart-btn, .refresh-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.restart-btn {
  background: #dc3545;
  color: white;
}

.restart-btn:hover:not(:disabled) {
  background: #c82333;
}

.restart-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.refresh-btn {
  background: #6c757d;
  color: white;
}

.refresh-btn:hover {
  background: #5a6268;
}

.connection-log {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.connection-log h4 {
  margin: 0;
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  color: #495057;
}

.log-container {
  max-height: 200px;
  overflow-y: auto;
  padding: 10px 20px;
}

.log-entry {
  display: flex;
  gap: 10px;
  padding: 4px 0;
  font-size: 12px;
  border-bottom: 1px solid #f8f9fa;
}

.log-time {
  color: #6c757d;
  min-width: 80px;
}

.log-message {
  color: #495057;
}

/* 加载动画 */
.status-buffering .status-label {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style> 