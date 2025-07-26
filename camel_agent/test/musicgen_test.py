import asyncio
from google import genai
from google.genai import types
import os

# 设置 API key
API_KEY = "AIzaSyBBdBeKuXNqgzp_zzv1UsiOcGI8EKLanMQ"

# 初始化客户端
client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1alpha'})

async def main():
    # 定义音频处理函数
    async def receive_audio(session):
        """处理接收到的音频数据"""
        try:
            while True:
                async for message in session.receive():
                    # 获取音频数据
                    audio_data = message.server_content.audio_chunks[0].data
                    # 这里可以添加音频处理逻辑,比如保存到文件或播放
                    print("收到音频数据块...")
                    await asyncio.sleep(10**-12)
        except Exception as e:
            print(f"接收音频时出错: {e}")

    try:
        # 创建音乐生成会话
        async with (
            client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
            asyncio.TaskGroup() as tg,
        ):
            # 设置接收音频的任务
            tg.create_task(receive_audio(session))

            # 设置音乐生成提示词
            await session.set_weighted_prompts(
                prompts=[
                    types.WeightedPrompt(text='轻柔的钢琴曲', weight=1.0),
                    types.WeightedPrompt(text='冥想音乐', weight=0.8),
                ]
            )

            # 设置音乐生成配置
            await session.set_music_generation_config(
                config=types.LiveMusicGenerationConfig(
                    bpm=80,  # 设置曲速
                    temperature=0.8  # 设置创造性程度
                )
            )

            print("开始生成音乐...")
            # 开始生成音乐
            await session.play()
            
            # 让音乐生成运行一段时间
            await asyncio.sleep(30)  # 生成30秒音乐
            
    except Exception as e:
        print(f"生成音乐时出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())