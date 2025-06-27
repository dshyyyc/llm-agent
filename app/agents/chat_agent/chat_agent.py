import logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.llms.llm_factory import get_llm
from app.agents.chat_agent.schema import ChatRequest, ChatResponse
from app.services import conversation_service

logger = logging.getLogger(__name__)


async def run_chat_agent(current_state: dict, query: str) -> dict:
    """
    运行有记忆的Chat Agent。

    Args:
        current_state: 当前的会话状态，期望包含一个 'messages' 列表。
        query: 用户的最新输入。

    Returns:
        一个包含更新后 'messages' 列表的新状态字典。
    """
    logger.info(f"Chat Agent 收到用户查询: '{query}'")

    history = current_state.get("messages", [])

    # 如果是新对话，添加系统消息
    if not history:
        history.append(
            SystemMessage(content="你是一个乐于助人的AI助手，请简明扼要地回答问题。")
        )

    # 将当前用户输入添加到历史记录中
    history.append(HumanMessage(content=query))

    llm = get_llm("deepseek")

    # 使用 MessagesPlaceholder 来容纳可变长度的历史消息
    prompt_template = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
        ]
    )

    parser = StrOutputParser()
    chain = prompt_template | llm | parser

    # 异步调用链，并传入完整的消息历史
    result = await chain.ainvoke({"chat_history": history})
    logger.info(f"Chat Agent 生成的回复: '{result}'")

    # 将AI的回复也添加到历史记录中
    history.append(AIMessage(content=result))

    # 返回更新后的完整状态
    return {"messages": history}


async def handle_chat_request(request: ChatRequest) -> ChatResponse:
    """
    处理对Chat Agent的完整请求，封装了状态管理和响应格式化的所有逻辑。
    """
    logger.info(
        f"处理Chat Agent请求: conversation_id='{request.conversation_id}', query='{request.query}'"
    )

    # 1. 获取或创建会话状态
    conversation_id, current_state = (
        await conversation_service.get_or_create_conversation_state(
            request.conversation_id, agent_type="chat"
        )
    )

    # 2. 调用Agent核心逻辑
    final_state = await run_chat_agent(current_state, request.query)

    # 3. 从最终状态中提取最新的AI回复
    ai_reply = ""
    if final_state.get("messages") and isinstance(
        final_state["messages"][-1], AIMessage
    ):
        ai_reply = final_state["messages"][-1].content
    else:
        logger.error(
            f"在Chat会话 {conversation_id} 的最终状态中未找到AIMessage: {final_state}"
        )
        ai_reply = "抱歉，处理您的请求时出现了一点问题。"

    # 4. 更新会话状态
    await conversation_service.update_conversation_state(
        conversation_id, final_state, agent_type="chat"
    )
    logger.info(f"更新并保存Chat会话 {conversation_id} 的状态。")

    # 5. 返回标准响应体
    return ChatResponse(response=ai_reply, conversation_id=conversation_id)
