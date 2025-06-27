from contextvars import ContextVar
from typing import Optional

# 定义一个ContextVar，类型为 Optional[str]，默认值为 None
# 当不在请求上下文中时，它的值就是 None
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)