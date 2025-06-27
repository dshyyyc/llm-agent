import uvicorn
import uuid
from fastapi import FastAPI, Request
from app.api.endpoints import agents  # 导入我们定义的路由模块
from app.core.logging_config import setup_logging
from app.core.context import request_id_var
import logging

setup_logging()

logger = logging.getLogger(__name__)


# 1. 初始化FastAPI应用
app = FastAPI(
    title="简单多Agent项目",
    description="一个用于演示多Agent调用的基础FastAPI结构。",
    version="1.0.0",
)


# --- 添加中间件 (Middleware) ---
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    # 为每个请求生成一个唯一的ID
    request_id = str(uuid.uuid4())

    # 将 request_id 设置到 context var 中。
    # .set() 方法会返回一个 token，用于之后重置变量
    token = request_id_var.set(request_id)

    # 在响应头中也添加这个ID，方便前端或调用方进行调试
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    # 请求处理完毕后，重置 context var
    request_id_var.reset(token)

    return response

# 2. 将路由包含到主应用中
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])

# 3. 定义根路径
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "欢迎来到Agent服务，请访问 /docs 查看API文档。"}


# 4. 添加启动服务的入口点
if __name__ == "__main__":
    # 使用 uvicorn.run() 以编程方式启动服务
    # host="0.0.0.0" 让服务在你的网络中可访问
    # reload=True 会在代码更改时自动重启服务，非常适合开发
    print("🚀 服务启动中... API文档请访问: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)