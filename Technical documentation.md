# 项目技术文档

## 1. 项目简介

本项目是一款创新的对话式互动游戏，融合了用户输入的故事背景、对话内容与Emotiv脑机接口实时采集的EEG脑电数据（情绪映射），通过AI技术和脑机情绪实时驱动剧情走向、图片背景和音乐氛围。项目采用前后端分离与微服务架构，支持多模态交互体验。

---

## 2. 系统架构

### 2.1 总体架构

```
┌────────────┐   用户输入/EEG   ┌────────────┐   AI生成   ┌────────────┐
│  前端界面   │───────────────→ │  后端服务   │─────────→  │ AI模型/服务 │
└────────────┘                └────────────┘           └────────────┘
      ↑                             ↑
      └───────── WebSocket/HTTP ────┘
```

-   **前端**：负责用户输入、对话展示、图片/音乐渲染、EEG状态监控。
-   **后端**：负责EEG数据采集与情绪识别、AI代理工作流管理、剧情生成、图片生成、音乐生成服务的编排与调度。
-   **AI服务**：包括文本生成（剧情）、图片生成、实时音乐生成等AI模型（如Azure OpenAI GPT-4）。

---

## 3. 主要模块与技术细节

### 3.1 前端（frontend/）

-   **技术栈**：Vue 3、Vite、WebSocket、Fetch API
-   **主要功能**：
    -   用户输入背景、对话。
    -   实时展示AI生成的剧情、图片、音乐氛围。
    -   监控EEG情绪状态（通过WebSocket与后端通信）。
    -   音乐状态监控与错误处理。
-   **关键组件**：
    -   `AudioStatusMonitor.vue`：实时音频状态与情绪监控。
    -   `AIChat.vue`：对话交互界面。
    -   `TheWelcome.vue`、`Loading.vue`：界面辅助组件。

#### 3.1.1 EEG情绪映射与前端联动

-   前端通过WebSocket监听后端推送的情绪状态（如`valence`、`arousal`、`emotion`标签），并据此动态调整界面提示。
-   剧情、图片、音乐的最终效果由后端AI代理根据情绪综合生成，前端负责接收并渲染。

---

### 3.2 后端

后端系统采用分层设计，包括负责底层数据和硬件交互的 **基础服务层**，以及负责核心逻辑和工作流编排的 **AI代理层**。

#### 3.2.1 基础服务层 (Infrastructure Services)

此层面负责与外部设备（EEG）和专项AI服务（音乐生成）直接交互。

-   **技术栈**：Python 3.8+、FastAPI、Uvicorn、Pydantic、sounddevice、numpy、websocket-client、requests
-   **主要服务模块**：
    -   `brain_processor.py`：EEG数据采集与情绪识别。
    -   `audio_service.py`：音乐生成与播放控制。
    -   `cortex.py`：Emotiv Cortex SDK集成。
    -   `start_services.py`：服务启动与管理。

##### 3.2.1.1 EEG数据采集与情绪识别

-   通过Emotiv Cortex SDK采集EEG脑电波数据。
-   实时分析EEG信号，计算情绪指标（如Valence效价、Arousal唤醒度）。
-   **情绪识别算法**：本系统采用Valence（效价）和Arousal（唤醒度）两个维度对EEG脑波数据进行情绪识别。先根据EEG原始指标加权计算Valence和Arousal（范围-1~1），再用`atan2(arousal, valence)`得到角度，按区间分配情绪标签。情绪强度低于阈值时，统一归为“中性”。
-   **情绪标签映射表**：

| 角度区间（度） | 英文标签 | 中文标签 |
| :---: | :---: | :---: |
| 0~30 | Happy | 开心 |
| 30~60 | Excited | 激动 |
| 60~90 | Surprised | 惊讶 |
| 90~112.5 | Fear | 恐惧 |
| 112.5~135 | Angry | 愤怒 |
| 135~157.5 | Contempt | 轻蔑 |
| 157.5~180 | Disgust | 厌恶 |
| 180~198 | Miserable | 痛苦 |
| 198~216 | Sad | 悲伤 |
| 216~234 | Depressed | 沮丧 |
| 234~252 | Bored | 无聊 |
| 252~270 | Tired | 疲惫 |
| 270~300 | Sleepy | 困倦 |
| 300~330 | Relaxed | 放松 |
| 330~360 | Pleased | 满足 |
| 其它/低强度 | Neutral | 中性 |

##### 3.2.1.2 音乐生成服务

-   接收情绪数据，调用Google Lyria等AI音乐生成模型，动态调整音乐风格与参数。
-   **音乐风格与情绪的映射规则**：情绪标签会进一步映射为详细的音乐风格参数（如基调、乐器、节奏、氛围等），用于生成AI音乐Prompt。

| 情绪标签 | 基础风格 | 乐器 | 节奏 | 动态 | 氛围 | 织体 |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| 开心 (Happy) | 明亮大调，欢快旋律 | 钢琴、弦乐、吉他 | 120-140 BPM | 渐强，活泼 | 欢欣鼓舞 | 丰富分层 |
| 激动 (Excited) | 动感节奏，和弦推进 | 电吉他、鼓、合成器 | 140-160 BPM | 高能，戏剧性 | 紧张激烈 | 密集有力 |
| 悲伤 (Sad) | 小调，忧郁旋律 | 钢琴、大提琴、小提琴 | 50-70 BPM | 柔和，情感丰富 | 深沉忧伤 | 简约抒情 |
| 愤怒 (Angry) | 激烈和弦，强烈节奏 | 失真吉他、重鼓、铜管 | 150-180 BPM | 大声，冲击力强 | 激烈对抗 | 厚重密集 |
| 恐惧 (Fear) | 黑暗小调，色彩和声 | 低音弦乐、铜管、打击 | 70-120 BPM | 突变，紧张 | 阴森悬疑 | 渐进层次 |
| ... | ... | ... | ... | ... | ... | ... |

-   详细参数可参考`audio_service.py`中的`COMPLEX_EMOTION_MAPPING`字典。

#### 3.2.2 AI代理与工作流层 (AI Agent & Workflow)

**概述**
本层基于 **CAMEL-AI** 框架实现了一个核心AI代理系统，负责整个交互式体验的逻辑控制。它整合了故事生成、图像生成、音乐生成和记忆管理功能，使用 Azure OpenAI 的 GPT-4 模型作为核心驱动，并通过模块化的工具包与基础服务层交互。

##### 3.2.2.1 核心组件

1.  **代理核心 (Agent Core - `workflows/main.py`, `workflows/api.py`)**
    *   实现主要代理工作流和 REST API 端点。
    *   管理对话流程，整合用户输入、情绪数据和记忆。
    *   调用各类工具包（Toolkits）完成多模态内容生成。

2.  **记忆系统 (Memory System - `memory/memory.py`)**
    *   维护对话历史、故事背景、角色信息和用户偏好。
    *   实现记忆锚点以在长对话中保持上下文。
    *   提供记忆的检索与存储功能。

3.  **工具包 (Toolkits)**
    *   **图像生成 (`toolkits/imgen_tool.py`)**: 接收代理的指令（如场景描述），调用外部服务（如Stable Diffusion）生成图像。
    *   **音乐生成 (`toolkits/musicgen_tool.py`)**: 处理从代理传入的EEG情绪数据，生成音乐参数，并与`audio_service.py`通信以生成和播放音乐。
    *   **记忆工具包 (`toolkits/__init__.py`)**: 为代理提供管理和查询记忆系统的接口。

##### 3.2.2.2 主要特性

1.  **对话管理**: 故事驱动的对话系统，具备上下文感知能力，能整合用户偏好和跟踪场景进度。
2.  **记忆管理**: 分类存储故事、角色、场景、偏好等记忆，支持选择性检索。
3.  **多模态生成**: 基于文本、情绪和记忆，统一调度故事、图像和音乐的生成。

##### 3.2.2.3 技术规格

-   **环境配置**:
    ```python
    # Azure OpenAI 配置
    AZURE_OPENAI_ENDPOINT = "https://ai-philxia4932ai122623990161.openai.azure.com/"
    AZURE_API_VERSION = "2024-02-15-preview"
    AZURE_DEPLOYMENT_NAME = "gpt-4.1"
    ```
-   **模型配置**:
    ```python
    {
        "model_type": ModelType.GPT_4O_MINI,
        "model_config_dict": {
            "temperature": 0.8,
            "max_tokens": 1200,
            "top_p": 0.95,
            "stream": False
        }
    }
    ```

##### 3.2.2.4 实现细节与最佳实践

-   **代理初始化**: 启动时，代理会初始化Azure OpenAI模型，加载所有工具包，并建立记忆系统。
-   **错误处理**: 系统内置全面的错误捕获机制，确保服务的稳定性。
-   **响应生成**: 代理根据当前上下文、记忆和实时情绪，生成连贯且个性化的故事响应。

---

## 4. 数据流与交互流程

1.  用户在前端佩戴EEG设备，并输入初始故事背景或对话。
2.  **EEG数据流**：后端`brain_processor.py`实时采集EEG数据，识别出情绪标签（如"开心"）。
3.  **用户输入流**：前端将用户的文本消息通过HTTP POST请求发送到后端AI代理的`/api/chat`接口。
4.  **AI代理处理**：
    *   AI代理（`main.py`）接收到用户消息。
    *   它从`brain_processor.py`获取最新的情绪数据。
    *   它查询**记忆系统**，获取历史对话和故事背景。
    *   代理将用户输入、情绪、记忆整合后，向GPT-4模型请求生成下一步的剧情、场景描述和角色对话。
    *   代理根据GPT-4返回的结果，调用**图像生成工具包**（`imgen_tool.py`）和**音乐生成工具包**（`musicgen_tool.py`）。
5.  **多模态内容生成与展示**：
    *   音乐工具包将情绪传递给`audio_service.py`，生成并播放匹配的音乐。
    *   图像工具包生成新的背景图片。
    *   AI代理将生成的剧情文本、图片URL等信息作为响应返回给前端。
6.  前端接收到所有更新，实时渲染新的剧情、图片和音乐氛围，完成一次交互闭环。

---

## 5. API接口文档

### 5.1 基础服务API (主要供内部调用)

-   `GET /health`：健康检查。
-   `POST /update_emotion`：接收情绪数据（由`brain_processor`调用）。
-   `GET /audio_status`：获取音频流状态。
-   `POST /restart_audio`：重启音频服务。
-   `WebSocket /ws/audio_status`：实时推送音频状态给前端。

### 5.2 核心AI代理API (供前端调用)

-   **聊天交互接口**
    -   **Endpoint**: `POST /api/chat`
    -   **Content-Type**: `application/json`
    -   **Request Body**:
        ```json
        {
          "message": "string"
        }
        ```
    -   **Response Body**:
        ```json
        {
          "story_text": "string",
          "image_url": "string",
          "emotion_detected": "string"
        }
        ```

---

## 6. 配置与部署

### 6.1 环境依赖

-   Python依赖见`EEG/requirements.txt`及CAMEL-AI项目相关依赖。
-   Node.js依赖见`frontend/package.json`。

### 6.2 启动流程

1.  配置环境变量（如Azure OpenAI密钥）。
2.  安装后端依赖：`pip install -r requirements.txt`。
3.  安装前端依赖：在`frontend/`目录下执行 `npm install`。
4.  启动后端服务：`python start_services.py` (启动基础服务) 和 `python workflows/api.py` (启动AI代理API服务)。
5.  启动前端服务：在`frontend/`目录下执行 `npm run dev`。

---

## 7. 关键技术点与展望

-   **实时性**：系统的核心挑战在于保证EEG数据处理、AI决策和多模态内容生成的低延迟，为用户提供流畅的实时互动体验。
-   **上下文管理**：长程记忆系统（`memory.py`）对于维持故事的连贯性和深度至关重要。
-   **情绪映射精度**：EEG情绪识别的准确性直接影响音乐、剧情的匹配度，是保障用户体验的关键方向。

---

## 8. 参考与扩展

-   Emotiv Cortex SDK官方文档
-   CAMEL-AI官方文档
-   Azure OpenAI Service文档
-   Vue 3官方文档
-   FastAPI官方文档

---

