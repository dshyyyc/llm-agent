from fastapi import APIRouter
from app.agents.router_agent.schema import RouterChatRequest, RouterChatResponse
from app.agents.chat_agent.schema import ChatRequest, ChatResponse
from app.agents.chat_agent.chat_agent import handle_chat_request
from app.agents.router_agent.router_agent import handle_router_request
from app.services import conversation_service

# 创建一个路由实例
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="与有记忆的Chat Agent对话")
async def basic_chat(request: ChatRequest) -> ChatResponse:
    """
    将请求直接转发给Chat Agent的处理函数。
    API层只负责路由和数据校验，所有业务逻辑都在Agent内部处理。
    """
    return await handle_chat_request(request)


@router.post(
    "/router", response_model=RouterChatResponse, summary="与有状态的Router Agent交互"
)
async def router_agent_chat(req: RouterChatRequest) -> RouterChatResponse:
    """
    将请求直接转发给Router Agent的处理函数。
    API层只负责路由和数据校验，所有业务逻辑都在Agent内部处理。
    """
    return await handle_router_request(req)


@router.get("/stats", summary="获取会话统计信息")
async def get_conversation_stats():
    """
    获取各agent类型的会话统计信息，用于调试和监控。
    """
    stats = await conversation_service.get_conversation_stats()
    return {
        "message": "会话统计信息",
        "stats": stats,
        "total_conversations": sum(stats.values()),
    }
