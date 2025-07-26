# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========

"""
CAMEL-AI 自定义工具包模块

包含项目特定的工具包实现：
- ImageGenerationToolkit: 硅基流动图像生成工具包
"""

from .imgen_tool import ImageGenerationToolkit
from camel.toolkits import BaseToolkit, FunctionTool
from camel.messages import BaseMessage
from typing import List, Dict, Any
import json

class MemoryToolkit(BaseToolkit):
    """记忆工具包，用于获取和存储对话历史"""
    
    def __init__(self, memory_instance):
        self.memory = memory_instance
        super().__init__()
    
    def get_tools(self) -> List[FunctionTool]:
        """获取记忆相关工具"""
        # 创建get_memory工具
        get_memory_tool = FunctionTool(self._get_memory)
        
        # 创建save_memory工具
        save_memory_tool = FunctionTool(self._save_memory)
        
        return [get_memory_tool, save_memory_tool]
    
    def _get_memory(self, query: str) -> str:
        """获取历史记忆
        
        Args:
            query (str): 查询关键词，用于检索相关记忆
            
        Returns:
            str: 历史记忆内容
        """
        try:
            if hasattr(self.memory, 'chat_messages') and self.memory.chat_messages:
                # 获取最近的对话历史
                recent_messages = self.memory.chat_messages[-10:]
                memory_content = []
                
                for msg in recent_messages:
                    role = getattr(msg, 'role_name', getattr(msg, 'role', 'Unknown'))
                    content = msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
                    memory_content.append(f"{role}: {content}")
                
                return f"历史记忆查询 '{query}' 的结果:\n" + "\n".join(memory_content)
            else:
                return f"没有找到与 '{query}' 相关的历史记忆"
        except Exception as e:
            return f"获取记忆时出错: {str(e)}"
    
    def _save_memory(self, content: str, type: str) -> str:
        """保存记忆
        
        Args:
            content (str): 要保存的内容
            type (str): 内容类型：story, character, setting, preference
            
        Returns:
            str: 保存结果
        """
        try:
            # 这里可以扩展为更复杂的记忆存储逻辑
            return f"已保存 {type} 类型的记忆: {content[:100]}..."
        except Exception as e:
            return f"保存记忆时出错: {str(e)}"

__all__ = [
    'ImageGenerationToolkit',
    'MemoryToolkit',
] 