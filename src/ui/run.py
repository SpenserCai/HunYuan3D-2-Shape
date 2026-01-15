#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gradio UI 启动脚本

使用方式:
    # 仅启动 UI (连接到已运行的后端)
    python -m src.ui.run --api-url http://localhost:8000
    
    # 同时启动后端和 UI
    python -m src.ui.run --start-backend
    
    # 指定端口
    python -m src.ui.run --port 7860 --api-url http://localhost:8000
    
    # 创建公共链接
    python -m src.ui.run --share
"""

import argparse
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ui.app import launch_app


def main():
    parser = argparse.ArgumentParser(
        description="Hunyuan3D Shape Generation Gradio UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 连接到本地后端
  python -m src.ui.run
  
  # 连接到远程后端
  python -m src.ui.run --api-url http://192.168.1.100:8000
  
  # 同时启动后端服务
  python -m src.ui.run --start-backend
  
  # 创建公共分享链接
  python -m src.ui.run --share
        """
    )
    
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="后端 API 服务器地址 (默认: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--start-backend",
        action="store_true",
        help="同时启动后端 API 服务器"
    )
    
    parser.add_argument(
        "--weights-dir",
        type=str,
        default="weights",
        help="模型权重目录 (默认: weights)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="UI 服务器监听地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="UI 服务器监听端口 (默认: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="创建 Gradio 公共分享链接"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎨 Hunyuan3D Shape Generation UI")
    print("=" * 60)
    print(f"API 服务器: {args.api_url}")
    print(f"UI 地址: http://{args.host}:{args.port}")
    print(f"启动后端: {'是' if args.start_backend else '否'}")
    print("=" * 60)
    
    launch_app(
        api_url=args.api_url,
        start_backend=args.start_backend,
        weights_dir=args.weights_dir,
        host=args.host,
        port=args.port,
        share=args.share
    )


if __name__ == "__main__":
    main()
