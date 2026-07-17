"""Telegram 企业版机器人 - 消息处理器"""
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode

from config import Config, DataStore
from modes import ModeManager, MODE_WORK, MODE_REST
from calculators import ExchangeCalculator
from memo import MemoManager

logger = logging.getLogger(__name__)

# ──────────────── 自定义关键词管理 ────────────────

class KeywordManager:
    """触发关键词（自定义）管理 - 特别提醒主人"""

    @staticmethod
    def get_keywords() -> list:
        return DataStore.load("keywords", {"keywords": []}).get("keywords", [])

    @staticmethod
    def add_keyword(keyword: str) -> bool:
        keywords = KeywordManager.get_keywords()
        if keyword in keywords:
            return False
        keywords.append(keyword)
        DataStore.save("keywords", {"keywords": keywords})
        return True

    @staticmethod
    def remove_keyword(keyword: str) -> bool:
        keywords = KeywordManager.get_keywords()
        if keyword not in keywords:
            return False
        keywords.remove(keyword)
        DataStore.save("keywords", {"keywords": keywords})
        return True

    @staticmethod
    def list_keywords() -> str:
        keywords = KeywordManager.get_keywords()
        if not keywords:
            return "📋 当前没有设置触发关键词"
        text = "📋 **自定义触发关键词列表**\n\n"
        for i, kw in enumerate(keywords, 1):
            text += f"{i}. `{kw}`\n"
        text += "\n💡 匹配到关键词时会特别提醒主人查看"
        return text


# ──────────────── 休息模式自动回复 ────────────────

class RestModeReply:
    """休息模式自动回复管理"""

    @staticmethod
    def get_reply() -> str:
        return DataStore.load("rest_reply", {}).get(
            "reply", Config.REST_MODE_REPLY
        )

    @staticmethod
    def set_reply(text: str):
        DataStore.save("rest_reply", {"reply": text})

    @staticmethod
    def get_mention_keywords() -> list:
        """获取@主人时的关键词匹配列表"""
        return DataStore.load("mention_keywords", {"keywords": []}).get("keywords", [])

    @staticmethod
    def add_mention_keyword(keyword: str) -> bool:
        kw = RestModeReply.get_mention_keywords()
        if keyword in kw:
            return False
        kw.append(keyword)
        DataStore.save("mention_keywords", {"keywords": kw})
        return True

    @staticmethod
    def remove_mention_keyword(keyword: str) -> bool:
        kw = RestModeReply.get_mention_keywords()
        if keyword not in kw:
            return False
        kw.remove(keyword)
        DataStore.save("mention_keywords", {"keywords": kw})
        return True


# ──────────────── 键盘菜单 ────────────────

def get_main_menu_keyboard():
    """获取主菜单键盘"""
    keyboard = [
        [InlineKeyboardButton("🚀 启动", callback_data="menu_start"),
         InlineKeyboardButton("⏹ 停止", callback_data="menu_stop")],
        [InlineKeyboardButton("📒 记事本", callback_data="menu_memo")],
        [InlineKeyboardButton("📐 计算助手", callback_data="menu_calc")],
        [InlineKeyboardButton("⚙️ 关键词管理", callback_data="menu_keywords")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ──────────────── 菜单回调处理 ────────────────

async def menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_start":
        ModeManager.set_mode(MODE_REST)
        reply = RestModeReply.get_reply()
        await query.edit_message_text(
            f"✅ **休息模式已启动**\n\n"
            f"自动回复：{reply}\n\n"
            f"当有人私聊或@主人时，机器人将自动回复。\n"
            f"检测到自定义关键词时将特别提醒主人。",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    elif data == "menu_stop":
        ModeManager.set_mode(MODE_WORK)
        await query.edit_message_text(
            "✅ **工作模式已切换**\n\n"
            "机器人已切换到工作模式，休息模式自动回复已关闭。\n"
            "📒 备忘录记事本功能不受模式限制，始终可用。",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    elif data == "menu_memo":
        memos = MemoManager.list_all(page=1)
        text = "📒 **备忘录记事本**\n\n"
        if memos["memos"]:
            for m in memos["memos"]:
                time_str = MemoManager.format_time(m["time"])
                text += f"`#{m['id']}` {m['content'][:50]}"
                text += f"{'...' if len(m['content']) > 50 else ''}"
                text += f"  _{time_str}_\n"
            text += f"\n共 {memos['total']} 条备忘"
        else:
            text += "暂无备忘录\n"
        text += "\n\n**使用方式：**\n"
        text += "· `记 内容` — 添加备忘录\n"
        text += "· `删 编号` — 删除备忘录\n"
        text += "· `备忘录` — 查看全部\n"
        text += "· `清空备忘` — 清空所有"
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    elif data == "menu_calc":
        await query.edit_message_text(
            ExchangeCalculator.format_help(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    elif data == "menu_keywords":
        text = "⚙️ **关键词管理**\n\n"
        text += "**自定义触发关键词**（匹配到后特别提醒主人）：\n"
        for kw in KeywordManager.get_keywords():
            text += f"· `{kw}`\n"
        text += "\n**使用方式：**\n"
        text += "· `加关键词 词1 词2` — 添加\n"
        text += "· `删关键词 词1` — 删除\n"
        text += "· `查看关键词` — 查看全部\n"
        text += "· `设置回复 内容` — 设置休息模式自动回复"
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )


# ──────────────── 消息路由 ────────────────

async def message_handler(update: Update, context: CallbackContext):
    """统一消息处理器"""
    msg = update.message
    if not msg or not msg.text:
        return

    text = msg.text.strip()
    user_id = msg.from_user.id
    chat_type = msg.chat.type
    chat_id = msg.chat.id
    is_owner = (user_id == Config.OWNER_ID)
    is_private = (chat_type == "private")

    # ========== 主人专属命令（任何模式下都响应） ==========
    if is_owner:
        # 菜单
        if text == "/menu" or text == "菜单":
            await msg.reply_text(
                "🤖 **企业版机器人控制面板**\n\n"
                f"当前模式：{'🛌 休息模式' if ModeManager.is_rest_mode() else '💼 工作模式'}\n"
                "📒 备忘录记事本功能始终可用，不受模式限制",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard(),
            )
            return

        # 模式切换
        if text == "/start" or text == "启动":
            ModeManager.set_mode(MODE_REST)
            reply = RestModeReply.get_reply()
            await msg.reply_text(
                f"✅ 已切换到休息模式\n自动回复：{reply}",
            )
            return

        if text == "/stop" or text == "停止":
            ModeManager.set_mode(MODE_WORK)
            await msg.reply_text("✅ 已切换到工作模式，休息模式自动回复已关闭。\n📒 备忘录记事本功能始终可用，不受模式影响。")
            return

        # 设置回复内容
        set_reply_match = re.match(r"^设置回复\s+(.+)", text)
        if set_reply_match:
            content = set_reply_match.group(1).strip()
            RestModeReply.set_reply(content)
            await msg.reply_text(f"✅ 休息模式自动回复已设置为：\n{content}")
            return

        # 关键词管理
        if text == "查看关键词" or text == "/keywords":
            await msg.reply_text(KeywordManager.list_keywords(), parse_mode=ParseMode.MARKDOWN)
            return

        add_kw = re.match(r"^加关键词\s+(.+)", text)
        if add_kw:
            words = add_kw.group(1).strip().split()
            added = []
            for w in words:
                if KeywordManager.add_keyword(w.strip()):
                    added.append(w.strip())
            if added:
                await msg.reply_text(f"✅ 已添加触发关键词：{'、'.join(added)}")
            else:
                await msg.reply_text("⚠️ 关键词已存在或格式错误")
            return

        del_kw = re.match(r"^删关键词\s+(.+)", text)
        if del_kw:
            word = del_kw.group(1).strip()
            if KeywordManager.remove_keyword(word):
                await msg.reply_text(f"✅ 已删除触发关键词：{word}")
            else:
                await msg.reply_text("⚠️ 未找到该关键词")
            return

        # 计算助手
        if text == "/calc" or text == "计算":
            await msg.reply_text(
                ExchangeCalculator.format_help(),
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # 计算解析
        calc_result = ExchangeCalculator.parse_calculation(text)
        if calc_result:
            await msg.reply_text(calc_result, parse_mode=ParseMode.MARKDOWN)
            return

        # ========== 备忘录功能（所有模式均可用） ==========

        # 添加备忘录
        memo_content = MemoManager.parse_add_command(text)
        if memo_content:
            memo_id = MemoManager.add(memo_content)
            await msg.reply_text(f"✅ 已记录备忘录 #{memo_id}")
            return

        # 删除备忘录
        memo_del = MemoManager.parse_delete_command(text)
        if memo_del is not None:
            if MemoManager.delete(memo_del):
                await msg.reply_text(f"✅ 已删除备忘录 #{memo_del}")
            else:
                await msg.reply_text(f"⚠️ 未找到编号 #{memo_del} 的备忘录")
            return

        # 查看备忘录
        if text == "备忘录" or text == "记事本" or text == "/memo":
            memos = MemoManager.list_all(page=1)
            text_reply = "📒 **备忘录列表**\n\n"
            if memos["memos"]:
                for m in memos["memos"]:
                    time_str = MemoManager.format_time(m["time"])
                    text_reply += f"`#{m['id']}` {m['content']}  _{time_str}_\n"
                text_reply += f"\n共 {memos['total']} 条备忘"
            else:
                text_reply += "暂无备忘录"
            await msg.reply_text(text_reply, parse_mode=ParseMode.MARKDOWN)
            return

        if text == "清空备忘" or text == "清空记事本":
            MemoManager.clear()
            await msg.reply_text("✅ 已清空所有备忘录")
            return

        # 搜索备忘录
        search_match = re.match(r"^搜索\s+(.+)", text)
        if search_match:
            keyword = search_match.group(1).strip()
            results = MemoManager.search(keyword)
            if results:
                text_reply = f"🔍 搜索「{keyword}」结果：\n\n"
                for m in results:
                    time_str = MemoManager.format_time(m["time"])
                    text_reply += f"`#{m['id']}` {m['content']}  _{time_str}_\n"
                await msg.reply_text(text_reply, parse_mode=ParseMode.MARKDOWN)
            else:
                await msg.reply_text(f"❌ 未找到包含「{keyword}」的备忘录")
            return

        # 页码翻页
        page_match = re.match(r"^备忘录\s*(\d+)$", text)
        if page_match:
            page = int(page_match.group(1))
            memos = MemoManager.list_all(page=page)
            text_reply = f"📒 **备忘录列表 (第{memos['page']}/{memos['total_pages']}页)**\n\n"
            if memos["memos"]:
                for m in memos["memos"]:
                    time_str = MemoManager.format_time(m["time"])
                    text_reply += f"`#{m['id']}` {m['content']}  _{time_str}_\n"
                text_reply += f"\n共 {memos['total']} 条备忘"
            else:
                text_reply += "暂无备忘录"
            await msg.reply_text(text_reply, parse_mode=ParseMode.MARKDOWN)
            return

    # ========== 休息模式 — 自动回复 & 特别提醒 ==========
    if ModeManager.is_rest_mode() and not is_owner:
        # 检测是否私聊主人
        if is_private:
            # 自动回复
            reply_text = RestModeReply.get_reply()
            await msg.reply_text(reply_text)

            # 检测自定义触发关键词 — 特别提醒主人
            keywords = KeywordManager.get_keywords()
            matched_keywords = [kw for kw in keywords if kw in text]
            if matched_keywords:
                alert_msg = (
                    f"🚨 **特别提醒！**\n\n"
                    f"检测到触发关键词：{'、'.join(matched_keywords)}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 用户：{msg.from_user.full_name} (ID: {user_id})\n"
                    f"💬 内容：{text[:200]}\n"
                    f"📱 来源：私聊"
                )
                await context.bot.send_message(
                    chat_id=Config.OWNER_ID,
                    text=alert_msg,
                    parse_mode=ParseMode.MARKDOWN,
                )
            return

        # 检测群组/频道中 @主人
        if chat_type in ("group", "supergroup", "channel"):
            mention = f"@{Config.OWNER_USERNAME}"
            if mention in text:
                # 自动回复
                reply_text = RestModeReply.get_reply()
                await msg.reply_text(reply_text)

                # 特别提醒主人
                alert_msg = (
                    f"🚨 **有人@主人！**\n\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 用户：{msg.from_user.full_name} (ID: {user_id})\n"
                    f"💬 内容：{text[:200]}\n"
                    f"📢 群组：{msg.chat.title or msg.chat.effective_name} (ID: {chat_id})"
                )

                # 检测自定义关键词
                keywords = KeywordManager.get_keywords()
                matched_keywords = [kw for kw in keywords if kw in text]
                if matched_keywords:
                    alert_msg += f"\n⚠️ 匹配触发关键词：{'、'.join(matched_keywords)}"

                await context.bot.send_message(
                    chat_id=Config.OWNER_ID,
                    text=alert_msg,
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

    # ========== 工作模式 ==========
    if ModeManager.is_work_mode() and not is_owner:
        # 工作模式 — 非主人无额外操作（备忘录功能独立于模式，始终可用）
        pass


async def help_handler(update: Update, context: CallbackContext):
    """帮助命令"""
    msg = update.message
    if not msg:
        return
    help_text = (
        "🤖 **企业版 Telegram 机器人 — 帮助**\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "**菜单按钮**\n"
        "· `菜单` / `/menu` - 打开控制面板\n"
        "· `启动` / `/start` - 切换到休息模式\n"
        "· `停止` / `/stop` - 切换到工作模式\n\n"
        "**📒 备忘录记事本**\n"
        "· `记 内容` - 添加备忘录\n"
        "· `删 编号` - 删除备忘录\n"
        "· `备忘录` / `记事本` - 查看全部\n"
        "· `备忘录 N` - 查看第N页\n"
        "· `搜索 关键词` - 搜索备忘录\n"
        "· `清空备忘` - 清空所有\n\n"
        "**📐 计算助手**\n"
        "· `实时 7 交易 8.5` - 计算点位\n"
        "· `点位 17 实时 7` - 反算汇率\n"
        "· `/calc` / `计算` - 查看帮助\n\n"
        "**⚙️ 关键词管理**\n"
        "· `加关键词 词1 词2` - 添加触发词\n"
        "· `删关键词 词1` - 删除触发词\n"
        "· `查看关键词` - 查看所有\n"
        "· `设置回复 内容` - 设置自动回复\n\n"
        "**💡 模式说明**\n"
        "· 工作模式：安静模式，仅响应主人命令\n"
        "· 休息模式：自动回复 + 关键词特别提醒\n"
        "· 📒 备忘录记事本功能始终可用，不受模式限制"
    )
    await msg.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def unknown_handler(update: Update, context: CallbackContext):
    """未知命令处理"""
    msg = update.message
    if msg and msg.text:
        await msg.reply_text(
            "❓ 未知命令，发送 `菜单` 或 `/menu` 查看可用功能",
            parse_mode=ParseMode.MARKDOWN,
        )