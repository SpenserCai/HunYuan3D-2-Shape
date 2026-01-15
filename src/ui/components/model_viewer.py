# -*- coding: utf-8 -*-
"""
3D 模型预览组件
"""

import gradio as gr
from typing import Optional
import tempfile
import os


# 模型查看器占位符 HTML
MODEL_VIEWER_PLACEHOLDER = """
<div style="
    height: 500px; 
    width: 100%; 
    border-radius: 12px; 
    border: 2px dashed #e5e7eb; 
    display: flex; 
    justify-content: center; 
    align-items: center;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
">
    <div style="text-align: center; padding: 40px;">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" style="margin-bottom: 16px;">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>
        <p style="color: #64748b; font-size: 18px; font-weight: 500; margin: 0 0 8px 0;">
            欢迎使用 Hunyuan3D
        </p>
        <p style="color: #94a3b8; font-size: 14px; margin: 0;">
            上传图像并点击生成按钮开始创建 3D 模型
        </p>
    </div>
</div>
"""


def create_model_viewer_html(model_url: str, height: int = 500) -> str:
    """
    创建 model-viewer HTML
    
    Args:
        model_url: 模型文件 URL
        height: 查看器高度
        
    Returns:
        HTML 字符串
    """
    return f"""
    <div style="height: {height}px; width: 100%; border-radius: 12px; overflow: hidden; background: #1a1a2e;">
        <model-viewer
            src="{model_url}"
            alt="3D Model"
            auto-rotate
            camera-controls
            shadow-intensity="1"
            exposure="0.8"
            environment-image="neutral"
            style="width: 100%; height: 100%;"
        >
            <div class="progress-bar hide" slot="progress-bar">
                <div class="update-bar"></div>
            </div>
        </model-viewer>
    </div>
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
    """


def create_model_viewer() -> gr.HTML:
    """
    创建 3D 模型查看器组件
    
    Returns:
        Gradio HTML 组件
    """
    return gr.HTML(
        value=MODEL_VIEWER_PLACEHOLDER,
        label="3D 模型预览",
        elem_classes=["model-viewer-container"]
    )


def create_processing_html(message: str = "正在生成中...") -> str:
    """
    创建处理中状态的 HTML
    
    Args:
        message: 显示的消息
        
    Returns:
        HTML 字符串
    """
    return f"""
    <div style="
        height: 500px; 
        width: 100%; 
        border-radius: 12px; 
        border: 2px solid #3b82f6; 
        display: flex; 
        justify-content: center; 
        align-items: center;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    ">
        <div style="text-align: center; padding: 40px;">
            <div style="
                width: 60px; 
                height: 60px; 
                border: 4px solid #e5e7eb; 
                border-top: 4px solid #3b82f6; 
                border-radius: 50%; 
                animation: spin 1s linear infinite;
                margin: 0 auto 20px auto;
            "></div>
            <p style="color: #1e40af; font-size: 18px; font-weight: 500; margin: 0 0 8px 0;">
                {message}
            </p>
            <p style="color: #3b82f6; font-size: 14px; margin: 0;">
                这可能需要几分钟时间，请耐心等待
            </p>
        </div>
    </div>
    <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    """


def create_error_html(error_message: str) -> str:
    """
    创建错误状态的 HTML
    
    Args:
        error_message: 错误消息
        
    Returns:
        HTML 字符串
    """
    return f"""
    <div style="
        height: 500px; 
        width: 100%; 
        border-radius: 12px; 
        border: 2px solid #ef4444; 
        display: flex; 
        justify-content: center; 
        align-items: center;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    ">
        <div style="text-align: center; padding: 40px;">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" style="margin-bottom: 16px;">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <p style="color: #b91c1c; font-size: 18px; font-weight: 500; margin: 0 0 8px 0;">
                生成失败
            </p>
            <p style="color: #dc2626; font-size: 14px; margin: 0; max-width: 400px; word-wrap: break-word;">
                {error_message}
            </p>
        </div>
    </div>
    """
