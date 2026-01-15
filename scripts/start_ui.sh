#!/bin/bash
# 启动 Gradio UI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 默认参数
API_URL="${API_URL:-http://localhost:8000}"
UI_PORT="${UI_PORT:-7860}"
START_BACKEND="${START_BACKEND:-false}"

echo "=============================================="
echo "🎨 Hunyuan3D Shape Generation UI"
echo "=============================================="
echo "API URL: $API_URL"
echo "UI Port: $UI_PORT"
echo "Start Backend: $START_BACKEND"
echo "=============================================="

if [ "$START_BACKEND" = "true" ]; then
    python -m src.ui.run --api-url "$API_URL" --port "$UI_PORT" --start-backend
else
    python -m src.ui.run --api-url "$API_URL" --port "$UI_PORT"
fi
