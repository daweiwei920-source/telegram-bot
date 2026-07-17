"""Telegram 企业版机器人 - Render 健康检查服务"""
import os
import socket
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 10000))

# 事件，用于通知主线程健康检查服务已就绪
server_ready = threading.Event()


class HealthHandler(BaseHTTPRequestHandler):
    """健康检查端点"""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ok", "service": "telegram-bot-enterprise"}')

    def log_message(self, format, *args):
        logger.debug(f"Health check: {format % args}")


def _find_free_port(start_port):
    """从指定端口开始查找可用端口"""
    port = start_port
    while port < start_port + 100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return port
        except OSError:
            port += 1
    raise RuntimeError(f"无法找到可用端口（从 {start_port} 开始）")


def run_health_server():
    """
    启动健康检查 HTTP 服务器。
    使用 threading.Event 通知主线程服务器已就绪。
    """
    try:
        actual_port = _find_free_port(PORT)
        server = HTTPServer(("0.0.0.0", actual_port), HealthHandler)
        logger.info(f"✅ 健康检查服务已启动，监听端口 {actual_port}")
        # 通知主线程：端口已绑定
        server_ready.set()
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ 健康检查服务启动失败: {e}")
        # 即使失败也要通知主线程，避免死锁
        server_ready.set()