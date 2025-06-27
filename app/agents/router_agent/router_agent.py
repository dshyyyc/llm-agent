import os
import logging
from typing import TypedDict, Optional, Annotated

from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.agents.router_agent.schema import RouterChatRequest, RouterChatResponse
from app.services import conversation_service


logger = logging.getLogger(__name__)


# --- 状态定义 ---
class AgentState(TypedDict):
    input_file_link: Optional[str]
    operation_type: Optional[str]
    output_format: Optional[str]
    messages: Annotated[list, add_messages]


# --- 信息提取模型 ---
class Information(BaseModel):
    """从用户对话中提取的信息。"""

    is_relevant: bool = Field(
        True,
        description="用户输入是否与文档处理相关（总结、翻译、PPT生成等）。如果用户询问其他无关内容（如写代码、聊天等），应设为False。",
    )
    input_file_link: Optional[str] = Field(
        None, description="用户提供的输入文件的URL链接。"
    )
    operation_type: Optional[str] = Field(
        None,
        description="用户想要执行的操作，必须是 '总结', '翻译', 或 'ppt生成' 之一。",
    )
    output_format: Optional[str] = Field(
        None, description="用户指定的输出文件格式，例如 'docx', 'pptx'。"
    )


# --- LLM 初始化 ---
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-abe1bd4a7ea0465cbd5d5ed8e19f62b7",
    base_url="https://api.deepseek.com",
    temperature=0.7,
)
# structured_llm 仅负责从历史对话中提取所需信息，与对话llm是两部分
structured_llm = llm.with_structured_output(Information, method="function_calling")


# --- Agent 节点 ---
async def agent_node(state: AgentState):
    """
    核心Agent节点，负责思考、提取信息，并生成回复。
    """
    # 使用异步调用 structured_llm
    extracted_info = await structured_llm.ainvoke(state["messages"])

    # 首先检查用户输入是否与文档处理相关
    if not extracted_info.is_relevant:
        response_prompt = """你是一个专门处理文档内容的助手。用户询问的内容与文档处理无关。

        请礼貌地告知用户你只处理文档相关的内容（如文档总结、翻译、PPT生成等），并建议他们：
        1. 如果是编程相关问题，请使用专门的编程助手
        2. 如果是其他问题，请使用通用聊天助手
        3. 如果确实需要文档处理服务，请提供文件链接

        请用友好、专业的语气回复。
        """

        response = await llm.ainvoke([HumanMessage(content=response_prompt)])
        ai_message_content = response.content.strip()

        return {
            "input_file_link": state.get("input_file_link"),
            "operation_type": state.get("operation_type"),
            "output_format": state.get("output_format"),
            "messages": [AIMessage(content=ai_message_content)],
        }

    current_state = state.copy()
    if extracted_info.input_file_link:
        current_state["input_file_link"] = extracted_info.input_file_link
    if extracted_info.operation_type:
        current_state["operation_type"] = extracted_info.operation_type
    if extracted_info.output_format:
        current_state["output_format"] = extracted_info.output_format

    if not current_state.get("input_file_link"):
        response_prompt = (
            "你是一个友好的助手。请礼貌地询问用户需要处理的文件的链接是什么。"
        )
    elif not current_state.get("operation_type"):
        response_prompt = "你是一个友好的助手。已收到文件链接。请询问用户希望进行哪种操作（例如：总结、翻译、生成PPT）。"
    elif not current_state.get("output_format"):
        response_prompt = f"你是一个友好的助手。用户已指定操作为 '{current_state['operation_type']}'。请询问他们希望输出什么格式的文件（例如：docx, pptx）。"
    else:
        response_prompt = f"""你是一个友好的助手。所有信息都已收集完毕：
        - 文件链接: {current_state['input_file_link']}
        - 操作类型: {current_state['operation_type']}
        - 输出格式: {current_state['output_format']}
        请向用户确认这些信息，并告知他们你即将开始处理。"""

    # 使用异步调用 llm
    response = await llm.ainvoke([HumanMessage(content=response_prompt)])
    ai_message_content = response.content.strip()

    return {
        "input_file_link": current_state.get("input_file_link"),
        "operation_type": current_state.get("operation_type"),
        "output_format": current_state.get("output_format"),
        "messages": [AIMessage(content=ai_message_content)],
    }


# --- API 调用节点 ---
async def api_caller_node(state: AgentState):
    """
    API调用节点，在收集完所有信息后触发。
    """
    api_url = os.getenv("DOC_GENERATION_API_URL", "http://example.com/generate")
    payload = {
        "input_file_link": state["input_file_link"],
        "operation_type": state["operation_type"],
        "output_format": state["output_format"],
    }
    # 在生产环境中，这里应该是实际的API调用
    # 如果需要异步HTTP调用，可以使用 aiohttp 或 httpx
    # response = await httpx.AsyncClient().post(api_url, json=payload)
    message_content = f"文档生成任务已模拟启动！将使用以下信息处理: {payload}"
    return {"messages": [AIMessage(content=message_content)]}


# --- 条件判断边 ---
def should_continue(state: AgentState) -> str:
    """条件判断函数，决定下一步走向。"""
    if (
        state.get("input_file_link")
        and state.get("operation_type")
        and state.get("output_format")
    ):
        return "call_api"
    else:
        return "continue"


# --- 构建并编译图 ---
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("api_caller", api_caller_node)
graph_builder.set_entry_point("agent")

graph_builder.add_conditional_edges(
    "agent", should_continue, {"continue": END, "call_api": "api_caller"}
)
graph_builder.add_edge("api_caller", END)
compiled_graph = graph_builder.compile()


# --- Agent 入口函数 ---
async def run_router_agent(current_state: dict, user_input: str) -> dict:
    """
    运行Router Agent的核心逻辑。

    Args:
        current_state: 当前会话的状态。
        user_input: 用户的最新输入。

    Returns:
        更新后的最终状态。
    """
    # 将用户的输入添加到消息历史中
    current_state["messages"].append(HumanMessage(content=user_input))

    # 使用异步调用 LangGraph 应用
    final_state = await compiled_graph.ainvoke(current_state)

    return final_state


async def handle_router_request(req: RouterChatRequest) -> RouterChatResponse:
    """
    处理对Router Agent的完整请求，封装了状态管理和响应格式化的所有逻辑。
    """
    logger.info(
        f"处理Router Agent请求: conversation_id='{req.conversation_id}', user_input='{req.user_input}'"
    )

    # 1. 获取或创建会话状态
    conversation_id, current_state = (
        await conversation_service.get_or_create_conversation_state(
            req.conversation_id, agent_type="router"
        )
    )

    # 2. 调用Agent核心逻辑
    final_state = await run_router_agent(current_state, req.user_input)

    # 3. 从最终状态中提取最新的AI回复
    ai_reply = ""
    if final_state.get("messages") and isinstance(
        final_state["messages"][-1], AIMessage
    ):
        ai_reply = final_state["messages"][-1].content
    else:
        logger.error(
            f"在Router会话 {conversation_id} 的最终状态中未找到AIMessage: {final_state}"
        )
        ai_reply = "抱歉，我好像遇到了一点问题，没能生成回复。"

    # 4. 更新会话状态
    await conversation_service.update_conversation_state(
        conversation_id, final_state, agent_type="router"
    )
    logger.info(f"更新并保存Router会话 {conversation_id} 的状态。")

    # 5. 返回响应
    return RouterChatResponse(reply=ai_reply, conversation_id=conversation_id)
