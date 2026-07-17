# Telegram 企业版机器人

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

功能强大的 Telegram 企业版机器人，支持工作/休息双模式、备忘录记事本、点位汇率计算、关键词提醒等功能。

## 功能特性

### 双模式切换
- **工作模式** 💼 — 安静模式，仅响应主人命令
- **休息模式** 🛌 — 自动回复 + 关键词特别提醒主人
- 📒 **备忘录记事本功能独立于模式，始终可用**

### 📒 备忘录记事本
- `记 内容` — 添加备忘录
- `删 编号` — 删除指定备忘录
- `备忘录` — 查看全部备忘录列表
- `搜索 关键词` — 搜索备忘录内容
- `清空备忘` — 清空所有备忘录

### 📐 点位与汇率计算
- **点位计算**：`实时 7 交易 8.5`
  - 公式：【1 - (实时汇率 ÷ 交易汇率)】× 100 = 点位
- **汇率反算**：`点位 17 实时 7`
  - 公式：1 - (点位÷100) = X，实时汇率 ÷ X = 汇率

### ⚙️ 关键词特别提醒
- `加关键词 词1 词2` — 添加触发关键词
- `删关键词 词1` — 删除触发关键词
- `查看关键词` — 查看所有关键词
- 休息模式中匹配到关键词时，自动回复并特别提醒主人

### 🎛 菜单按钮控制
- 🚀 启动 — 切换到休息模式
- ⏹ 停止 — 切换到工作模式
- 📒 记事本 — 查看备忘录
- 📐 计算助手 — 计算帮助
- ⚙️ 关键词管理 — 管理触发词

## 🚀 一键部署到 Render（推荐）

点击上方按钮或访问 [render.com/deploy](https://render.com/deploy) 导入此仓库，只需填写 3 个必填环境变量即可运行。

### 部署步骤

#### 1. 获取 Bot Token
在 Telegram 搜索 [@BotFather](https://t.me/BotFather)，创建新机器人，获取 Token。

#### 2. 获取用户 ID
在 Telegram 搜索 [@userinfobot](https://t.me/userinfobot)，发送任意消息，获取你的数字 ID。

#### 3. 打开 Render 部署页面
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

填入以下环境变量：

| 变量 | 说明 |
|------|------|
| `BOT_TOKEN` | 从 @BotFather 获取的 Token |
| `OWNER_ID` | 你的数字用户 ID |
| `OWNER_USERNAME` | 你的 Telegram 用户名（不带@） |

其余变量均有默认值，无需修改。点击 **Deploy Blueprint** 等待 2-3 分钟即可完成部署。

### 部署后注意事项
- 机器人使用 **Polling 模式**，Render 重启后会自动恢复
- 数据存储在 Render 磁盘中，部署更新后数据会保留
- 免费版 Render 实例 15 分钟无访问会休眠，有请求时自动唤醒（延迟约 30 秒）
- 如需保持在线，可设置 [UptimeRobot](https://uptimerobot.com) 每 10 分钟访问一次服务的 URL

## 本地运行

### 1. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
BOT_TOKEN=你的机器人Token
OWNER_ID=你的用户ID数字
OWNER_USERNAME=你的用户名
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动机器人
```bash
python main.py
```

## 配置文件 (.env)

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `BOT_TOKEN` | Telegram Bot Token | **必填** |
| `OWNER_ID` | 主人数字 ID | **必填** |
| `OWNER_USERNAME` | 主人用户名（不带@） | **必填** |
| `DEFAULT_MODE` | 默认模式（work/rest） | work |
| `REST_MODE_REPLY` | 休息模式自动回复内容 | 主人正在休息... |

## 目录结构

```
telegram-bot-enterprise/
├── main.py              # 主入口（含 Render 健康检查）
├── server.py            # Render 健康检查 HTTP 服务
├── config.py            # 配置管理 + JSON 持久化
├── modes.py             # 工作/休息模式管理
├── handlers.py          # 消息路由 + 菜单按钮
├── calculators.py       # 点位汇率计算
├── memo.py              # 备忘录记事本
├── render.yaml          # Render 一键部署配置
├── .env.example         # 配置模板
├── requirements.txt     # 依赖清单
└── data/                # 数据存储目录
    ├── mode.json        # 模式状态
    ├── memos.json       # 备忘录数据
    ├── keywords.json    # 关键词数据
    └── rest_reply.json  # 自动回复配置
```