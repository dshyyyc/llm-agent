from pydantic import BaseModel, Field


class RouterChatRequest(BaseModel):
    """定义有状态的Router Agent的请求体"""

    user_input: str = Field(..., example="我想要总结一个文件", description="用户的输入")
    conversation_id: str | None = Field(
        None,
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        description="会话ID，用于保持多轮对话的上下文",
    )


class RouterChatResponse(BaseModel):
    """定义有状态的Router Agent的响应体"""

    reply: str = Field(..., example="好的，请提供文件链接。", description="Agent的回复")
    conversation_id: str = Field(
        ..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef", description="本次会话的ID"
    )
