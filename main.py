"""Telegram 企业版机器人 - 主入口（适配 Render 部署）"""
import os
import sys
import threading
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import Config, logger
from handlers import (
    message_handler,
    help_handler,
    unknown_handler,
    menu_callback,
)
from server import run_health_server, server_ready


def main():
    """启动机器人（含 Render 健康检查服务）"""
    # ─── 配置验证 ───
    if not Config.validate():
        logger.error("❌ 配置验证失败！请检查 Render 环境变量：BOT_TOKEN、OWNER_ID、OWNER_USERNAME")
        # Render 需要端口绑定才能通过健康检查，即使配置失败也要启动 HTTP 服务
        _start_health_server_only()
        sys.exit(1)

    logger.info("=" * 40)
    logger.info("🤖 Telegram 企业版机器人 启动中...")
    logger.info(f"👤 主人 ID: {Config.OWNER_ID}")
    logger.info(f"📧 主人用户名: @{Config.OWNER_USERNAME}")
    logger.info(f"📋 默认模式: {Config.DEFAULT_MODE}")
    logger.info("=" * 40)

    # ─── 第1步：优先启动健康检查 HTTP 服务 ───
    logger.info("🌐 正在启动健康检查服务...")
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # 等待服务器就绪（最多等 10 秒）
    if not server_ready.wait(timeout=10):
        logger.warning("⚠️ 健康检查服务启动超时，继续启动 Bot...")

    # ─── 第2步：构建 Bot Application ───
    logger.info("🤖 正在构建 Telegram Bot Application...")
    app = Application.builder().token(Config.BOT_TOKEN).post_init(setup_commands).build()

    # 注册命令处理器
    app.add_handler(CommandHandler("start", message_handler))
    app.add_handler(CommandHandler("stop", message_handler))
    app.add_handler(CommandHandler("menu", message_handler))
    app.add_handler(CommandHandler("memo", message_handler))
    app.add_handler(CommandHandler("calc", message_handler))
    app.add_handler(CommandHandler("keywords", message_handler))
    app.add_handler(CommandHandler("help", help_handler))

    # 菜单回调处理器
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))

    # 文本消息处理器
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # 未知命令处理器
    app.add_handler(MessageHandler(filters.COMMAND, unknown_handler))

    # ─── 第3步：启动 Polling ───
    logger.info("🚀 机器人已就绪，开始轮询 Telegram 消息...")
    logger.info("💡 发送 /menu 或「菜单」打开控制面板")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


async def setup_commands(app: Application):
    """设置 Telegram 机器人左下角菜单按钮命令列表"""
    commands = [
        BotCommand("start", "🚀 启动（休息模式）"),
        BotCommand("stop", "⏹ 停止（工作模式）"),
        BotCommand("menu", "📋 控制面板"),
        BotCommand("memo", "📒 备忘录记事本"),
        BotCommand("calc", "📐 计算助手"),
        BotCommand("keywords", "⚙️ 关键词管理"),
        BotCommand("help", "❓ 帮助"),
    ]
    try:
        await app.bot.set_my_commands(commands)
        logger.info("✅ 机器人菜单命令已更新")
    except Exception as e:
        logger.warning(f"⚠️ 设置菜单命令失败: {e}")


def _start_health_server_only():
    """配置验证失败时，仅启动健康检查服务（防止 Render 放弃部署）"""
    try:
        import http.server
        port = int(os.environ.get("PORT", 10000))

        class ErrorHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "error", "message": "Missing BOT_TOKEN or OWNER_ID"}')
            def log_message(self, format, *args):
                pass

        server = http.server.HTTPServer(("0.0.0.0", port), ErrorHandler)
        logger.warning(f"⚠️ 配置验证失败，仅启动健康检查（端口 {port}），状态 503")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ 健康检查服务也启动失败: {e}")


if __name__ == "__main__":
    main()