from app.llms.deepseek import DeepSeekModel
from app.llms.qwen import QwenModel


def get_llm(model_type: str):
    """
    根据模型类型返回对应的 LLM 实例。
    """
    if model_type == "deepseek":
        deepseek_model = DeepSeekModel()
        return deepseek_model.get_model()
    elif model_type == "qwen":
        qwen_model = QwenModel()
        return qwen_model.get_model()
    else:
        raise ValueError(f"未知的模型类型: {model_type}")
