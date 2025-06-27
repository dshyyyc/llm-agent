from langchain_openai import ChatOpenAI
from app.core.config import MODEL_CONFIGS


class QwenModel:
    def __init__(self, temperature: float = 0.7):
        """
        :param temperature: 生成文本的随机性 (默认0.7)
        """
        config = MODEL_CONFIGS["qwen-max"]
        self._api_key = config["api_key"]
        self._base_url = config["base_url"]
        self._temperature = temperature
        self._model = self._initialize_model()

    def _initialize_model(self) -> ChatOpenAI:
        """私有方法：创建并返回 ChatOpenAI 实例"""
        return ChatOpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
            temperature=self._temperature,
            model_name="qwen-max"  # 默认模型，可根据需要修改
        )

    def get_model(self) -> ChatOpenAI:
        """
        获取初始化后的 LangChain ChatOpenAI 模型

        :return: 初始化完成的 ChatOpenAI 实例
        """
        return self._model
