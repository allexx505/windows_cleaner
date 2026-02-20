"""
本地日志配置：将应用与 uvicorn 的日志写入配置目录下的日志文件，便于问题排查。
使用 RotatingFileHandler 控制单文件大小与保留份数，避免占满磁盘。
"""
import logging
import os
from logging.handlers import RotatingFileHandler

# 应用主 logger 名称，业务代码可使用 get_logger(__name__) 或 get_logger("windows_cleaner")
LOGGER_NAME = "windows_cleaner"

# 单文件最大字节数，超过则轮转
LOG_FILE_MAX_BYTES = 2 * 1024 * 1024  # 2MB
# 保留的备份文件数量
LOG_BACKUP_COUNT = 5
# 日志文件名
LOG_FILE_NAME = "windows_cleaner.log"

# 文件格式：时间、级别、logger 名、消息
FILE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
# 日期格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_file_handler: RotatingFileHandler | None = None


def setup_logging(log_dir: str | None = None) -> str | None:
    """
    初始化本地日志：在 log_dir 下创建 logs 子目录，并配置写入轮转日志文件。
    同时将同一 handler 挂到 uvicorn 相关 logger 上，便于排查请求与错误。
    :param log_dir: 配置目录路径，若为 None 则使用 constants.CONFIG_DIR
    :return: 当前日志文件绝对路径，若未创建则返回 None
    """
    global _file_handler
    if log_dir is None:
        from backend.core.constants import CONFIG_DIR
        log_dir = CONFIG_DIR
    logs_dir = os.path.join(log_dir, "logs")
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except OSError:
        return None
    log_path = os.path.join(logs_dir, LOG_FILE_NAME)
    try:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError:
        return None
    handler.setFormatter(logging.Formatter(FILE_FORMAT, datefmt=DATE_FORMAT))
    handler.setLevel(logging.DEBUG)

    # 应用主 logger：记录业务与监控等
    app_logger = logging.getLogger(LOGGER_NAME)
    app_logger.setLevel(logging.DEBUG)
    app_logger.addHandler(handler)
    app_logger.propagate = False

    # 根 logger 也写一份，避免未指定 logger 的日志丢失
    root = logging.getLogger()
    root.addHandler(handler)

    # 让 uvicorn 的日志也写入同一文件，便于排查请求与启动错误（不向 root 传播，避免重复）
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.addHandler(handler)
        uvicorn_logger.propagate = False

    _file_handler = handler
    return os.path.abspath(log_path)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    获取用于输出日志的 logger。建议业务模块使用 get_logger(__name__)。
    :param name: 子名称，若为 None 则返回主应用 logger (windows_cleaner)
    """
    if name is None:
        return logging.getLogger(LOGGER_NAME)
    if name.startswith(LOGGER_NAME + ".") or name == LOGGER_NAME:
        return logging.getLogger(name)
    return logging.getLogger(LOGGER_NAME + "." + name)
