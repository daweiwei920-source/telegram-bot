"""Telegram 企业版机器人 - 点位与汇率计算"""
import re
import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class ExchangeCalculator:
    """业务点位与汇率计算工具"""

    @staticmethod
    def calculate_points(real_rate: float, trade_rate: float) -> float:
        """
        点位计算：
        【1 - (实时汇率 ÷ 交易汇率)】 × 100 = 点位

        例：实时汇率 7，交易汇率 8.5
        【1 - (7 ÷ 8.5)】 × 100 = 17.65 点位
        """
        if trade_rate == 0:
            raise ValueError("交易汇率不能为0")
        result = (1 - (real_rate / trade_rate)) * 100
        return round(result, 2)

    @staticmethod
    def calculate_rate(points: float, real_rate: float) -> float:
        """
        汇率计算：
        1 - (点位 ÷ 100) = X
        实时汇率 ÷ X = 汇率

        例：点位 17，实时汇率 7
        1 - (17 ÷ 100) = 0.83
        7 ÷ 0.83 = 8.43 汇率
        """
        divisor = 1 - (points / 100)
        if divisor == 0:
            raise ValueError("计算结果分母为0，请检查点位是否等于100")
        result = real_rate / divisor
        return round(result, 4)

    @staticmethod
    def parse_calculation(text: str) -> str:
        """智能解析用户输入，自动判断计算类型"""
        text = text.strip()

        # 尝试匹配汇率计算：格式如 "17 7" 或 "点位17 实时7" 或 "点位=17 实时=7"
        # 先尝试匹配点位计算：格式如 "实时7 交易8.5" 或 "实时=7 交易=8.5"
        point_match = re.search(
            r"(?:实时|现汇)[:=]?\s*(\d+\.?\d*)\s*(?:[,，;\s]+)\s*(?:交易|买入)[:=]?\s*(\d+\.?\d*)",
            text,
        )
        if point_match:
            real_rate = float(point_match.group(1))
            trade_rate = float(point_match.group(2))
            points = ExchangeCalculator.calculate_points(real_rate, trade_rate)
            return (
                f"📊 点位计算结果\n\n"
                f"实时汇率：{real_rate}\n"
                f"交易汇率：{trade_rate}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"点位：【1 - ({real_rate} ÷ {trade_rate})】× 100\n"
                f"= 【1 - {round(real_rate / trade_rate, 4)}】× 100\n"
                f"= {round(1 - real_rate / trade_rate, 4)} × 100\n"
                f"= **{points} 点位** 🎯"
            )

        # 尝试匹配汇率反算：格式如 "点位17 实时7" 或 "点位=17 实时=7"
        rate_match = re.search(
            r"(?:点位|点数)[:=]?\s*(\d+\.?\d*)\s*(?:[,，;\s]+)\s*(?:实时|现汇)[:=]?\s*(\d+\.?\d*)",
            text,
        )
        if rate_match:
            points = float(rate_match.group(1))
            real_rate = float(rate_match.group(2))
            trade_rate = ExchangeCalculator.calculate_rate(points, real_rate)
            return (
                f"📊 汇率计算结果\n\n"
                f"点位：{points}\n"
                f"实时汇率：{real_rate}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"X = 1 - ({points} ÷ 100) = {round(1 - points / 100, 4)}\n"
                f"汇率 = {real_rate} ÷ {round(1 - points / 100, 4)}\n"
                f"= **{trade_rate}** 💰"
            )

        return ""

    @staticmethod
    def format_help() -> str:
        return (
            "📐 **点位与汇率计算助手**\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "**① 点位计算**\n"
            "格式：`实时 7 交易 8.5`\n"
            "或：`实时=7 交易=8.5`\n"
            "公式：【1 - (实时÷交易)】× 100\n\n"
            "**② 汇率反算**\n"
            "格式：`点位 17 实时 7`\n"
            "或：`点位=17 实时=7`\n"
            "公式：1 - (点位÷100) = X，实时÷X = 汇率\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "💡 直接发送数字对即可自动判断"
        )