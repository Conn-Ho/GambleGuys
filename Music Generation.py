from google import genai
import os

client = genai.Client(api_key="AIzaSyBz3Gn7w5WaWzv167mo5PoXnXEodVwAEPE")  # 添加API密钥

import asyncio
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCypLd7vuyrUOE16_N9wwTYFx6EiPMEC1k")

async def main():
    async def receive_audio(session):
      """Example background task to process incoming audio."""
      while True:
        async for message in session.receive():
          audio_data = message.server_content.audio_chunks[0].data
          # Process audio...
          await asyncio.sleep(10**-12)

    async with (
      client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
      asyncio.TaskGroup() as tg,
    ):
      # Set up task to receive server messages.
      tg.create_task(receive_audio(session))

      # Send initial prompts and config
      await session.set_weighted_prompts(
        prompts=[
          types.WeightedPrompt(text='minimal techno', weight=1.0),
        ]
      )
      await session.set_music_generation_config(
        config=types.LiveMusicGenerationConfig(bpm=90, temperature=1.0)
      )
      # Start streaming music
      await session.play()
if __name__ == "__main__":
    asyncio.run(main())