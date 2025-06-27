import logging
import sys
from pathlib import Path
from app.core.context import request_id_var


APP_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = APP_DIR / "logs"
LOG_FILE = LOGS_DIR / "app.log"


class RequestIdFilter(logging.Filter):
    """
    这是一个日志过滤器，它会把 contextvars 中的 request_id 添加到日志记录中。
    """

    def filter(self, record):
        # 从 contextvars 获取 request_id，如果不存在则使用默认值 'N/A'
        record.request_id = request_id_var.get("N/A")
        return True


def setup_logging():
    """
    配置项目的日志记录器。
    """
    # --- 确保日志目录存在 ---
    # 使用 pathlib 的 mkdir 方法，更加简洁和安全
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 修改日志格式，加入 request_id
    log_format = '%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

    request_id_filter = RequestIdFilter()

    # --- 文件处理器 ---
    # 使用 pathlib 对象 LOG_FILE 作为路径
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.addFilter(request_id_filter)

    # --- 控制台处理器 ---
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(request_id_filter)

    # 清除并添加新的处理器
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    logging.info("日志系统配置完成，日志文件位于: " + str(LOG_FILE))