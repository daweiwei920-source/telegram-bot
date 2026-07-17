"""Telegram 企业版机器人 - 备忘录记事本"""
import re
import time
from config import DataStore
import logging

logger = logging.getLogger(__name__)

MAX_MEMOS = 200  # 最大备忘录条数
MEMO_MAX_LENGTH = 1000  # 单条最大长度


class MemoManager:
    """备忘录记事本管理"""

    @staticmethod
    def _get_all() -> dict:
        """获取所有备忘录"""
        return DataStore.load("memos", {"memos": [], "counter": 0})

    @staticmethod
    def _save_all(data: dict):
        DataStore.save("memos", data)

    @staticmethod
    def add(content: str) -> int:
        """添加备忘录，返回ID"""
        if len(content) > MEMO_MAX_LENGTH:
            raise ValueError(f"备忘录内容不能超过{MEMO_MAX_LENGTH}字")

        data = MemoManager._get_all()
        data["counter"] += 1
        memo_id = data["counter"]

        data["memos"].append({
            "id": memo_id,
            "content": content,
            "time": int(time.time()),
        })

        # 限制总数
        if len(data["memos"]) > MAX_MEMOS:
            data["memos"] = data["memos"][-MAX_MEMOS:]

        MemoManager._save_all(data)
        return memo_id

    @staticmethod
    def delete(memo_id: int) -> bool:
        """删除指定ID的备忘录"""
        data = MemoManager._get_all()
        original_len = len(data["memos"])
        data["memos"] = [m for m in data["memos"] if m["id"] != memo_id]
        if len(data["memos"]) == original_len:
            return False
        MemoManager._save_all(data)
        return True

    @staticmethod
    def clear():
        """清空所有备忘录"""
        MemoManager._save_all({"memos": [], "counter": 0})

    @staticmethod
    def list_all(page: int = 1, page_size: int = 10) -> dict:
        """分页列出备忘录"""
        data = MemoManager._get_all()
        memos = data["memos"]
        total = len(memos)

        start = (page - 1) * page_size
        end = start + page_size
        page_memos = memos[start:end]

        total_pages = max(1, (total + page_size - 1) // page_size)

        return {
            "memos": page_memos,
            "total": total,
            "page": page,
            "total_pages": total_pages,
        }

    @staticmethod
    def search(keyword: str) -> list:
        """搜索备忘录"""
        data = MemoManager._get_all()
        results = []
        for m in data["memos"]:
            if keyword in m["content"]:
                results.append(m)
        return results

    @staticmethod
    def format_time(timestamp: int) -> str:
        """格式化时间戳"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def parse_add_command(text: str) -> str:
        """解析 '记 内容' 格式的命令"""
        match = re.match(r"^记[录事]?\s+(.+)", text.strip())
        if match:
            return match.group(1).strip()
        return ""

    @staticmethod
    def parse_delete_command(text: str) -> int | None:
        """解析 '删 编号' 或 '删除 编号' 格式的命令"""
        match = re.match(r"^(?:删|删除|del)\s*(\d+)$", text.strip())
        if match:
            return int(match.group(1))
        return None