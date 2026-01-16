# -*- coding: utf-8 -*-
"""
设置面板组件
"""

import gradio as gr
from typing import Dict, Any, Tuple


# 支持的输出格式
SUPPORTED_FORMATS = ['glb', 'obj', 'ply', 'stl']

# 生成模式预设
GENERATION_PRESETS = {
    'fast': {'steps': 20, 'resolution': 256, 'label': '快速 (Fast)'},
    'standard': {'steps': 50, 'resolution': 384, 'label': '标准 (Standard)'},
    'quality': {'steps': 100, 'resolution': 512, 'label': '高质量 (Quality)'}
}

# 光照校正方法
LIGHTING_METHODS = [
    ('直方图匹配', 'histogram_matching'),
    ('颜色转移', 'color_transfer'),
    ('自动曝光', 'auto_exposure')
]


def create_generation_mode_selector() -> Tuple[gr.Radio, gr.Radio]:
    """
    创建生成模式选择器
    
    Returns:
        (生成模式, 分辨率模式) 组件元组
    """
    gen_mode = gr.Radio(
        label="生成模式",
        choices=[
            ('快速 (20步)', 'fast'),
            ('标准 (50步)', 'standard'),
            ('高质量 (100步)', 'quality')
        ],
        value='standard',
        info="推荐使用标准模式，快速模式适合预览"
    )
    
    resolution_mode = gr.Radio(
        label="分辨率模式",
        choices=[
            ('低 (256)', 'low'),
            ('标准 (384)', 'standard'),
            ('高 (512)', 'high')
        ],
        value='standard',
        info="更高分辨率生成更精细的模型，但需要更多时间"
    )
    
    return gen_mode, resolution_mode


def create_settings_panel() -> Dict[str, Any]:
    """
    创建完整的设置面板
    
    Returns:
        包含所有设置组件的字典
    """
    components = {}
    
    with gr.Accordion("基础设置", open=True):
        with gr.Row():
            components['remove_background'] = gr.Checkbox(
                label="移除背景",
                value=True,
                info="自动移除图像背景"
            )
            components['optimize_mesh'] = gr.Checkbox(
                label="优化网格",
                value=True,
                info="简化和优化生成的网格"
            )
    
    with gr.Accordion("高级设置", open=False):
        with gr.Row():
            components['num_inference_steps'] = gr.Slider(
                label="推理步数",
                minimum=1,
                maximum=200,
                value=50,
                step=1,
                info="更多步数通常产生更好的结果"
            )
            components['guidance_scale'] = gr.Slider(
                label="引导强度",
                minimum=0,
                maximum=20.0,
                value=5.0,
                step=0.5,
                info="控制生成结果与输入的相似度"
            )
        
        with gr.Row():
            components['octree_resolution'] = gr.Slider(
                label="八叉树分辨率",
                minimum=128,
                maximum=512,
                value=384,
                step=64,
                info="更高分辨率产生更精细的几何细节"
            )
            components['max_faces'] = gr.Slider(
                label="最大面数",
                minimum=1000,
                maximum=1000000,
                value=40000,
                step=1000,
                info="限制输出网格的面数"
            )
    
    with gr.Accordion("质量增强选项", open=False):
        gr.Markdown("*以下选项可提升生成质量，但会增加处理时间*")
        
        # 预处理增强（仅多视图模式）
        with gr.Group():
            gr.Markdown("**预处理增强** (多视图模式)")
            with gr.Row():
                components['normalize_lighting'] = gr.Checkbox(
                    label="光照一致性校正",
                    value=False,
                    info="统一多视图的光照条件"
                )
                components['lighting_method'] = gr.Dropdown(
                    label="校正方法",
                    choices=LIGHTING_METHODS,
                    value="histogram_matching",
                    info="选择光照校正算法"
                )
                components['lighting_strength'] = gr.Slider(
                    label="校正强度",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.8,
                    step=0.1,
                    info="0=不校正, 1=完全校正"
                )
        
        # 后处理增强
        with gr.Group():
            gr.Markdown("**后处理增强**")
            with gr.Row():
                components['fill_holes'] = gr.Checkbox(
                    label="填充孔洞",
                    value=False,
                    info="自动填充网格中的孔洞"
                )
                components['make_watertight'] = gr.Checkbox(
                    label="水密网格",
                    value=False,
                    info="生成封闭的水密网格"
                )
            with gr.Row():
                components['smooth_surface'] = gr.Checkbox(
                    label="表面平滑",
                    value=False,
                    info="平滑网格表面减少噪声"
                )
                components['smooth_iterations'] = gr.Slider(
                    label="平滑迭代",
                    minimum=1,
                    maximum=10,
                    value=2,
                    step=1,
                    info="平滑处理的迭代次数"
                )
            with gr.Row():
                components['recalculate_normals'] = gr.Checkbox(
                    label="重算法线",
                    value=False,
                    info="重新计算顶点和面法线"
                )
    
    with gr.Accordion("输出设置", open=False):
        components['output_format'] = gr.Dropdown(
            label="输出格式",
            choices=SUPPORTED_FORMATS,
            value="glb",
            info="GLB 格式兼容性最好"
        )
    
    return components


def get_preset_values(preset: str) -> Tuple[int, int]:
    """
    获取预设值
    
    Args:
        preset: 预设名称
        
    Returns:
        (推理步数, 分辨率) 元组
    """
    if preset == 'fast':
        return 20, 256
    elif preset == 'quality':
        return 100, 512
    else:  # standard
        return 50, 384
