#!/usr/bin/env python3
"""
测试脚本：验证 chat_agent 和 router_agent 的会话隔离功能
"""

import asyncio
import uuid
from app.agents.chat_agent.schema import ChatRequest
from app.agents.router_agent.schema import RouterChatRequest
from app.agents.chat_agent.chat_agent import handle_chat_request
from app.agents.router_agent.router_agent import handle_router_request
from app.services import conversation_service


async def test_conversation_isolation():
    """测试会话隔离功能"""
    print("🧪 开始测试会话隔离功能...")

    # 使用相同的 conversation_id 测试两个不同的 agent
    test_conversation_id = str(uuid.uuid4())
    print(f"📝 使用相同的 conversation_id: {test_conversation_id}")

    # 测试 Chat Agent
    print("\n1️⃣ 测试 Chat Agent:")
    chat_request = ChatRequest(
        query="你好，请介绍一下你自己", conversation_id=test_conversation_id
    )
    chat_response = await handle_chat_request(chat_request)
    print(f"   Chat Agent 回复: {chat_response.response}")
    print(f"   Chat Agent conversation_id: {chat_response.conversation_id}")

    # 测试 Router Agent
    print("\n2️⃣ 测试 Router Agent:")
    router_request = RouterChatRequest(
        user_input="我想要总结一个文档", conversation_id=test_conversation_id
    )
    router_response = await handle_router_request(router_request)
    print(f"   Router Agent 回复: {router_response.reply}")
    print(f"   Router Agent conversation_id: {router_response.conversation_id}")

    # 再次测试 Chat Agent，验证会话隔离
    print("\n3️⃣ 再次测试 Chat Agent (验证会话隔离):")
    chat_request2 = ChatRequest(
        query="我们刚才聊了什么？", conversation_id=test_conversation_id
    )
    chat_response2 = await handle_chat_request(chat_request2)
    print(f"   Chat Agent 回复: {chat_response2.response}")

    # 再次测试 Router Agent，验证会话隔离
    print("\n4️⃣ 再次测试 Router Agent (验证会话隔离):")
    router_request2 = RouterChatRequest(
        user_input="请提供文件链接", conversation_id=test_conversation_id
    )
    router_response2 = await handle_router_request(router_request2)
    print(f"   Router Agent 回复: {router_response2.reply}")

    # 查看会话统计
    print("\n📊 会话统计信息:")
    stats = await conversation_service.get_conversation_stats()
    for agent_type, count in stats.items():
        print(f"   {agent_type}: {count} 个会话")

    print("\n✅ 测试完成！")
    print(
        "💡 如果 Chat Agent 和 Router Agent 的对话历史没有相互干扰，说明会话隔离功能正常工作。"
    )


if __name__ == "__main__":
    asyncio.run(test_conversation_isolation())
