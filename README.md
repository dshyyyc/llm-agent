# LLM Agent 项目

这是一个基于 FastAPI 的 LLM Agent 项目，支持多种类型的 AI 代理进行对话交互。

## 功能特性

### 🤖 多 Agent 支持

- **Chat Agent**: 通用对话代理，支持多轮对话记忆
- **Router Agent**: 文档处理代理，支持文件总结、翻译、PPT 生成等功能

### 🔒 会话隔离

- 不同类型的 Agent 使用独立的会话存储空间
- 即使使用相同的 `conversation_id`，不同 Agent 的对话历史也不会相互干扰
- 支持会话统计和管理功能

## API 端点

### Chat Agent

- `POST /chat` - 与 Chat Agent 进行对话

### Router Agent

- `POST /router` - 与 Router Agent 进行交互

### 管理功能

- `GET /stats` - 获取各 Agent 类型的会话统计信息

## 会话隔离机制

### 问题背景

在之前的实现中，`chat_agent` 和 `router_agent` 共享同一个会话存储空间，当使用相同的 `conversation_id` 时会导致对话历史混淆。

### 解决方案

1. **分层存储结构**: 使用嵌套字典结构，按 Agent 类型隔离会话状态
2. **Agent 类型标识**: 每个 Agent 使用特定的类型标识符（"chat"、"router"）
3. **独立状态管理**: 不同类型的 Agent 拥有完全独立的会话状态

### 存储结构

```python
conversation_states = {
    "chat": {
        "conversation_id_1": {"messages": [...]},
        "conversation_id_2": {"messages": [...]}
    },
    "router": {
        "conversation_id_1": {"messages": [...], "input_file_link": "...", ...},
        "conversation_id_3": {"messages": [...], "operation_type": "...", ...}
    }
}
```

## 开发指南

### 运行测试

```bash
python test_conversation_isolation.py
```

### 添加新的 Agent 类型

1. 在 `conversation_service.py` 中为新 Agent 指定唯一的 `agent_type`
2. 在 Agent 处理函数中传入对应的 `agent_type` 参数
3. 确保新 Agent 的状态结构与现有 Agent 兼容

## 技术栈

- **FastAPI**: Web 框架
- **LangChain**: LLM 集成
- **LangGraph**: 工作流编排
- **Pydantic**: 数据验证
- **asyncio**: 异步编程

## 项目结构

```
app/
├── agents/           # Agent 实现
│   ├── chat_agent/   # 通用对话 Agent
│   └── router_agent/ # 文档处理 Agent
├── api/              # API 端点
├── services/         # 业务服务
├── llms/             # LLM 配置
└── core/             # 核心功能
```
