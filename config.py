"""Telegram 企业版机器人 - 配置文件管理"""
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# 数据文件目录
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
    OWNER_USERNAME = os.getenv("OWNER_USERNAME", "").lstrip("@")
    DEFAULT_MODE = os.getenv("DEFAULT_MODE", "work")
    REST_MODE_REPLY = os.getenv("REST_MODE_REPLY", "主人正在休息，稍后会回复您，请耐心等待。")
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            logger.error("BOT_TOKEN 未设置！请在 .env 文件中配置。")
            return False
        if not cls.OWNER_ID or cls.OWNER_ID == 0:
            logger.error("OWNER_ID 未设置！请在 .env 文件中配置。")
            return False
        return True


class DataStore:
    """基于 JSON 文件的持久化存储"""

    @staticmethod
    def _file_path(name: str) -> Path:
        return DATA_DIR / f"{name}.json"

    @staticmethod
    def load(name: str, default: any = None) -> any:
        path = DataStore._file_path(name)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default if default is not None else {}

    @staticmethod
    def save(name: str, data: any):
        path = DataStore._file_path(name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)