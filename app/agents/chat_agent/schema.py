from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """定义 Chat Agent 的请求体"""

    query: str = Field(
        ..., example="你好，最近过得怎么样？", description="用户的查询内容"
    )
    conversation_id: str | None = Field(
        None,
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        description="会话ID，用于保持多轮对话的上下文。如果是新对话则无需提供。",
    )


class ChatResponse(BaseModel):
    """定义 Chat Agent 的响应体"""

    response: str = Field(
        ..., example="我很好，感谢您的关心！", description="Agent生成的回复"
    )
    conversation_id: str = Field(
        ...,
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        description="本次会话的ID，用于后续对话",
    )
