#!/bin/bash
# 启动 API 服务器

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 默认参数
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"

echo "=============================================="
echo "🔧 Hunyuan3D Shape Generation API Server"
echo "=============================================="
echo "Host: $API_HOST"
echo "Port: $API_PORT"
echo "Docs: http://$API_HOST:$API_PORT/docs"
echo "=============================================="

python -m uvicorn src.api.server:app --host "$API_HOST" --port "$API_PORT" --reload
