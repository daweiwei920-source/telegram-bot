"""Telegram 企业版机器人 - 模式管理"""
from config import Config, DataStore
import logging

logger = logging.getLogger(__name__)

MODE_WORK = "work"
MODE_REST = "rest"

class ModeManager:
    """工作/休息模式管理"""

    @staticmethod
    def get_mode() -> str:
        """获取当前模式"""
        data = DataStore.load("mode", {"mode": Config.DEFAULT_MODE})
        return data.get("mode", Config.DEFAULT_MODE)

    @staticmethod
    def set_mode(mode: str) -> bool:
        """设置模式"""
        if mode not in (MODE_WORK, MODE_REST):
            logger.warning(f"无效模式: {mode}")
            return False
        DataStore.save("mode", {"mode": mode})
        logger.info(f"模式已切换为: {mode}")
        return True

    @staticmethod
    def is_work_mode() -> bool:
        return ModeManager.get_mode() == MODE_WORK

    @staticmethod
    def is_rest_mode() -> bool:
        return ModeManager.get_mode() == MODE_REST

    @staticmethod
    def toggle() -> str:
        """切换模式，返回新模式"""
        current = ModeManager.get_mode()
        new_mode = MODE_REST if current == MODE_WORK else MODE_WORK
        ModeManager.set_mode(new_mode)
        return new_mode