#!/bin/bash
# 同时启动 API 服务器和 Gradio UI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 默认参数
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
UI_PORT="${UI_PORT:-7860}"

echo "=============================================="
echo "🚀 Hunyuan3D Shape Generation - Full Stack"
echo "=============================================="
echo "API Server: http://$API_HOST:$API_PORT"
echo "UI Server: http://$API_HOST:$UI_PORT"
echo "=============================================="

# 启动 API 服务器 (后台运行)
echo "Starting API server..."
python -m uvicorn src.api.server:app --host "$API_HOST" --port "$API_PORT" &
API_PID=$!

# 等待 API 服务器启动
echo "Waiting for API server to start..."
sleep 5

# 检查 API 服务器是否启动成功
if ! kill -0 $API_PID 2>/dev/null; then
    echo "Error: API server failed to start"
    exit 1
fi

echo "API server started (PID: $API_PID)"

# 启动 UI
echo "Starting UI server..."
python -m src.ui.run --api-url "http://localhost:$API_PORT" --port "$UI_PORT"

# 清理
echo "Stopping API server..."
kill $API_PID 2>/dev/null || true
