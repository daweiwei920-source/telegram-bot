#!/bin/bash
# Telegram 企业版机器人 - 一键启动脚本
set -e

cd "$(dirname "$0")"

echo "=========================================="
echo " Telegram 企业版机器人 - 一键启动"
echo "=========================================="

# 1. 检查 .env
if [ ! -f .env ]; then
    echo "❌ 缺少 .env 文件"
    exit 1
fi

# 2. 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -q --break-system-packages 2>/dev/null

# 3. 启动
echo "🚀 启动机器人..."
python main.py