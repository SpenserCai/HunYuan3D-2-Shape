# -*- coding: utf-8 -*-
"""
状态面板组件
"""

import gradio as gr
from typing import Dict, Any, Optional


def create_status_panel() -> Dict[str, Any]:
    """
    创建状态面板
    
    Returns:
        包含状态组件的字典
    """
    components = {}
    
    with gr.Row():
        components['status_indicator'] = gr.HTML(
            value=create_status_html("未连接", "disconnected"),
            elem_classes=["status-indicator"]
        )
    
    with gr.Accordion("服务状态详情", open=False):
        components['health_info'] = gr.JSON(
            label="服务信息",
            value={}
        )
        components['refresh_btn'] = gr.Button(
            "刷新状态",
            size="sm",
            variant="secondary"
        )
    
    return components


def create_status_html(status_text: str, status_type: str = "normal") -> str:
    """
    创建状态指示器 HTML
    
    Args:
        status_text: 状态文本
        status_type: 状态类型 (connected, disconnected, processing, error)
        
    Returns:
        HTML 字符串
    """
    # 统一风格的颜色方案 - 蓝色/绿色系
    colors = {
        "connected": ("#10b981", "#ecfdf5", "#065f46"),      # 绿色 - 已连接
        "disconnected": ("#6b7280", "#f3f4f6", "#374151"),   # 灰色 - 未连接
        "processing": ("#3b82f6", "#eff6ff", "#1e40af"),     # 蓝色 - 处理中
        "error": ("#dc2626", "#fef2f2", "#991b1b")           # 红色 - 错误
    }
    
    dot_color, bg_color, text_color = colors.get(status_type, colors["disconnected"])
    
    return f"""
    <div style="
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        background: {bg_color};
        border-radius: 20px;
        gap: 8px;
    ">
        <span style="
            width: 10px;
            height: 10px;
            background: {dot_color};
            border-radius: 50%;
            display: inline-block;
        "></span>
        <span style="color: {text_color}; font-size: 14px; font-weight: 500;">
            {status_text}
        </span>
    </div>
    """


def format_health_info(health_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化健康检查信息
    
    Args:
        health_data: 原始健康数据
        
    Returns:
        格式化后的数据
    """
    if not health_data:
        return {"状态": "未知"}
    
    return {
        "服务状态": health_data.get("status", "未知"),
        "是否就绪": "是" if health_data.get("is_ready") else "否",
        "已加载模型": health_data.get("loaded_models", []),
        "GPU 显存使用": f"{health_data.get('gpu_memory_used_gb', 0):.2f} GB",
        "GPU 显存总量": f"{health_data.get('gpu_memory_total_gb', 0):.2f} GB"
    }
