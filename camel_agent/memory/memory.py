from camel.memories import (
    ChatHistoryMemory,
    ScoreBasedContextCreator,
)
from camel.utils import OpenAITokenCounter
from camel.types import ModelType

memory = ChatHistoryMemory(
    context_creator=ScoreBasedContextCreator(
        token_counter=OpenAITokenCounter(ModelType.GPT_4O_MINI),
        token_limit=2048,
    ),
    window_size=20
)

