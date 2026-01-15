# -*- coding: utf-8 -*-
"""
图像输入组件
"""

import gradio as gr
from typing import Tuple, Dict, Any


def create_single_image_input() -> gr.Image:
    """
    创建单图输入组件
    
    Returns:
        Gradio Image 组件
    """
    return gr.Image(
        label="输入图像",
        type="pil",
        image_mode="RGBA",
        height=320,
        sources=["upload", "clipboard"],
        elem_classes=["input-image"]
    )


def create_multi_view_input() -> Dict[str, gr.Image]:
    """
    创建多视图输入组件
    
    Returns:
        包含四个视角图像组件的字典
    """
    components = {}
    
    with gr.Row():
        components['front'] = gr.Image(
            label="正面 (Front) *必需",
            type="pil",
            image_mode="RGBA",
            height=160,
            min_width=120,
            sources=["upload", "clipboard"],
            elem_classes=["mv-image", "mv-front"]
        )
        components['back'] = gr.Image(
            label="背面 (Back)",
            type="pil",
            image_mode="RGBA",
            height=160,
            min_width=120,
            sources=["upload", "clipboard"],
            elem_classes=["mv-image", "mv-back"]
        )
    
    with gr.Row():
        components['left'] = gr.Image(
            label="左侧 (Left)",
            type="pil",
            image_mode="RGBA",
            height=160,
            min_width=120,
            sources=["upload", "clipboard"],
            elem_classes=["mv-image", "mv-left"]
        )
        components['right'] = gr.Image(
            label="右侧 (Right)",
            type="pil",
            image_mode="RGBA",
            height=160,
            min_width=120,
            sources=["upload", "clipboard"],
            elem_classes=["mv-image", "mv-right"]
        )
    
    return components
