import uuid
import asyncio
from typing import Dict, Any

# 使用嵌套字典来存储每个agent类型的会话状态
# 第一层键是 agent_type，第二层键是 conversation_id，值是该对话的 AgentState
conversation_states: Dict[str, Dict[str, Dict[str, Any]]] = {}

# 创建一个异步锁来确保对 conversation_states 的访问是线程安全的
conversation_lock = asyncio.Lock()


async def get_or_create_conversation_state(
    conversation_id: str | None, agent_type: str = "default"
) -> tuple[str, Dict[str, Any]]:
    """
    获取或创建一个新的会话状态。

    Args:
        conversation_id: 传入的会话ID，如果为None则创建一个新的。
        agent_type: agent类型，用于隔离不同agent的会话状态。

    Returns:
        一个元组，包含会话ID和对应的状态。
    """
    async with conversation_lock:
        # 确保该agent类型的存储空间存在
        if agent_type not in conversation_states:
            conversation_states[agent_type] = {}

        agent_states = conversation_states[agent_type]

        if not conversation_id or conversation_id not in agent_states:
            # 如果没有提供ID或ID不存在，则创建一个新的会话
            new_conversation_id = str(uuid.uuid4())
            # 初始化状态，只包含一个空的消息列表
            initial_state = {"messages": []}
            agent_states[new_conversation_id] = initial_state
            return new_conversation_id, initial_state
        else:
            # 如果提供了ID且存在，则返回现有的状态
            return conversation_id, agent_states[conversation_id]


async def update_conversation_state(
    conversation_id: str, new_state: Dict[str, Any], agent_type: str = "default"
):
    """
    更新指定会话的状态。

    Args:
        conversation_id: 要更新的会话的ID。
        new_state: 新的状态。
        agent_type: agent类型，用于隔离不同agent的会话状态。
    """
    async with conversation_lock:
        # 确保该agent类型的存储空间存在
        if agent_type not in conversation_states:
            conversation_states[agent_type] = {}

        conversation_states[agent_type][conversation_id] = new_state


async def get_conversation_stats() -> Dict[str, int]:
    """
    获取各agent类型的会话统计信息。

    Returns:
        包含各agent类型会话数量的字典。
    """
    async with conversation_lock:
        stats = {}
        for agent_type, agent_states in conversation_states.items():
            stats[agent_type] = len(agent_states)
        return stats


async def clear_conversation(conversation_id: str, agent_type: str = "default") -> bool:
    """
    清除指定会话的状态。

    Args:
        conversation_id: 要清除的会话ID。
        agent_type: agent类型。

    Returns:
        是否成功清除会话。
    """
    async with conversation_lock:
        if (
            agent_type in conversation_states
            and conversation_id in conversation_states[agent_type]
        ):
            del conversation_states[agent_type][conversation_id]
            return True
        return False


async def clear_all_conversations(agent_type: str = None):
    """
    清除所有会话或指定agent类型的所有会话。

    Args:
        agent_type: 如果指定，只清除该agent类型的会话；否则清除所有会话。
    """
    async with conversation_lock:
        if agent_type:
            if agent_type in conversation_states:
                conversation_states[agent_type].clear()
        else:
            conversation_states.clear()
