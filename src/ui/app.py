# -*- coding: utf-8 -*-
"""
Gradio 应用主入口
"""

import os
import sys
import tempfile
import base64
import time
import subprocess
import atexit
import shutil
import html
from typing import Optional, Dict, Any, Tuple

import gradio as gr
from PIL import Image

from .api_client import ShapeAPIClient
from .components.image_input import create_single_image_input, create_multi_view_input
from .components.settings_panel import create_settings_panel, SUPPORTED_FORMATS
from .components.status_panel import (
    create_status_panel,
    create_status_html,
    format_health_info
)


# 自定义 CSS - 全屏宽敞布局
CUSTOM_CSS = """
/* 全屏宽度 */
.gradio-container {
    max-width: 100% !important;
    padding: 20px 50px !important;
}

/* 主布局行 - 更大间距 */
.main-row {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 40px !important;
    padding: 20px 0 !important;
    align-items: flex-start !important;
}

/* 左侧列 - 固定宽度 */
.left-column {
    flex: 0 0 420px !important;
    min-width: 400px !important;
    max-width: 450px !important;
}

/* 右侧列 - 自适应填充 */
.right-column {
    flex: 1 1 auto !important;
    min-width: 700px !important;
}

/* 多视图图像样式 */
.mv-image button .wrap {
    font-size: 10px;
}
.mv-image .icon-wrap {
    width: 20px;
}

/* 3D 预览区域 */
.model-preview {
    min-height: 600px !important;
}

/* 生成按钮 */
.generate-btn {
    margin: 20px 0 !important;
    padding: 14px 24px !important;
    font-size: 17px !important;
    font-weight: 600 !important;
}
"""

# 标题 HTML - 更美观
TITLE_HTML = """
<div style="text-align: center; padding: 25px 0; margin-bottom: 15px;">
    <h1 style="font-size: 2.2em; font-weight: bold; margin: 0 0 10px 0; color: #fff;">
        🎨 Hunyuan3D Shape Generation
    </h1>
    <p style="color: #9ca3af; margin: 0; font-size: 1.05em;">
        高质量图像转 3D 模型生成服务 | 支持单图和多视图输入
    </p>
</div>
"""

# 3D 模型预览占位符 HTML
MODEL_VIEWER_PLACEHOLDER = """
<div style="
    height: 600px; 
    width: 100%; 
    border-radius: 12px; 
    border: 2px dashed #374151; 
    display: flex; 
    flex-direction: column;
    justify-content: center; 
    align-items: center;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    box-sizing: border-box;
">
    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="1.5" style="margin-bottom: 16px; display: block;">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
        <line x1="12" y1="22.08" x2="12" y2="12"/>
    </svg>
    <p style="color: #9ca3af; font-size: 18px; font-weight: 500; margin: 0 0 8px 0; text-align: center;">
        欢迎使用 Hunyuan3D
    </p>
    <p style="color: #6b7280; font-size: 14px; margin: 0; text-align: center;">
        上传图像并点击生成按钮开始创建 3D 模型
    </p>
</div>
"""

# model-viewer HTML 模板
MODEL_VIEWER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/@google/model-viewer@3.1.1/dist/model-viewer.min.js" type="module"></script>
    <style>
        body {{ margin: 0; background: #1a1a2e; }}
        .container {{ display: flex; justify-content: center; align-items: center; height: 100vh; }}
        model-viewer {{ width: 100%; height: 100%; --poster-color: transparent; }}
    </style>
</head>
<body>
<div class="container">
    <model-viewer 
        id="viewer"
        src="{model_path}"
        camera-controls
        auto-rotate
        rotation-per-second="30deg"
        shadow-intensity="1"
        environment-image="neutral"
        camera-orbit="0deg 75deg 105%"
        ar
    ></model-viewer>
</div>
</body>
</html>
"""


class GradioApp:
    """Gradio 应用类"""
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        start_backend: bool = False,
        weights_dir: str = "weights"
    ):
        self.api_url = api_url
        self.start_backend = start_backend
        self.weights_dir = weights_dir
        self.client = ShapeAPIClient(api_url)
        self.backend_process = None
        # 使用固定的静态文件目录
        self.static_dir = os.path.join(os.path.dirname(__file__), "static_models")
        os.makedirs(self.static_dir, exist_ok=True)
        self.temp_dir = tempfile.mkdtemp(prefix="hunyuan3d_ui_")
        
    def _start_backend_server(self):
        """启动后端 API 服务器"""
        if not self.start_backend:
            return
            
        print("正在启动后端 API 服务器...")
        
        from urllib.parse import urlparse
        parsed = urlparse(self.api_url)
        port = parsed.port or 8000
        
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.api.server:app",
            "--host", "0.0.0.0",
            "--port", str(port)
        ]
        
        # 不捕获输出，避免缓冲区满导致阻塞
        # 后端日志会直接输出到终端
        self.backend_process = subprocess.Popen(
            cmd,
            stdout=None,  # 直接输出到终端
            stderr=None   # 直接输出到终端
        )
        
        atexit.register(self._stop_backend_server)
        
        max_retries = 60
        for i in range(max_retries):
            time.sleep(1)
            response = self.client.health_check()
            if response.success:
                print("后端服务器启动成功!")
                return
            print(f"等待后端服务器启动... ({i+1}/{max_retries})")
        
        print("警告: 后端服务器可能未完全启动")
    
    def _stop_backend_server(self):
        """停止后端服务器"""
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("后端服务器已停止")
    
    def _build_model_viewer_html(self, model_path: str, height: int = 600) -> str:
        """
        构建 model-viewer HTML
        
        Args:
            model_path: 模型文件的 URL 路径（可以是 data URL 或文件路径）
            height: 查看器高度
            
        Returns:
            HTML 字符串
        """
        # 使用 srcdoc 创建 iframe，确保 model-viewer 脚本正确加载
        # 这种方式比直接在 Gradio HTML 中使用 script 标签更可靠
        iframe_content = f'''<!DOCTYPE html>
<html>
<head>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@3.1.1/dist/model-viewer.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }}
        model-viewer {{ width: 100%; height: 100vh; }}
    </style>
</head>
<body>
    <model-viewer
        src="{model_path}"
        alt="3D Model"
        auto-rotate
        rotation-per-second="30deg"
        camera-controls
        shadow-intensity="1"
        exposure="0.8"
        environment-image="neutral"
        camera-orbit="0deg 75deg 105%"
    ></model-viewer>
</body>
</html>'''
        
        # 对 iframe 内容进行 HTML 转义以用于 srcdoc
        import html
        escaped_content = html.escape(iframe_content)
        
        return f'''
        <div style="height: {height}px; width: 100%; border-radius: 12px; overflow: hidden;">
            <iframe 
                srcdoc="{escaped_content}"
                style="width: 100%; height: 100%; border: none;"
                allow="autoplay; fullscreen; xr-spatial-tracking"
            ></iframe>
        </div>
        '''
    
    def check_health(self) -> Tuple[str, Dict]:
        """检查服务健康状态"""
        response = self.client.health_check()
        
        if response.success:
            data = response.data
            status = data.get("status", "unknown")
            is_ready = data.get("is_ready", False)
            loaded_models = data.get("loaded_models", [])
            
            # 只要服务连通就显示已连接
            if is_ready and loaded_models:
                status_html = create_status_html(f"服务就绪 ({len(loaded_models)} 模型已加载)", "connected")
            elif status in ["healthy", "not_ready"]:
                # 服务已连接，模型会在首次请求时加载
                status_html = create_status_html("服务已连接", "connected")
            else:
                status_html = create_status_html("服务状态未知", "disconnected")
            
            return status_html, format_health_info(data)
        else:
            return create_status_html("连接失败", "error"), {"错误": response.error}
    
    def build_interface(self) -> gr.Blocks:
        """构建 Gradio 界面 - 左右布局"""
        
        # Gradio 6.0+: theme 和 css 需要在 launch() 中传递
        with gr.Blocks(
            title="Hunyuan3D Shape Generation",
            fill_width=True  # 使用全屏宽度
        ) as demo:
            # 标题 - 跨越整个宽度
            gr.HTML(TITLE_HTML)
            
            # 主要内容区域 - 左右布局
            with gr.Row(equal_height=False, elem_classes=["main-row"]):
                # ========== 左侧面板 - 输入和设置 ==========
                with gr.Column(scale=2, min_width=400, elem_classes=["left-column"]):
                    # 状态面板
                    status_components = create_status_panel()
                    
                    # 输入模式选择
                    with gr.Tabs(selected='tab_single') as input_tabs:
                        with gr.Tab('单图模式', id='tab_single'):
                            single_image = create_single_image_input()
                        
                        with gr.Tab('多视图模式', id='tab_multi_view'):
                            mv_images = create_multi_view_input()
                    
                    # 生成按钮
                    generate_btn = gr.Button(
                        "🚀 生成 3D 模型",
                        variant="primary",
                        elem_classes=["generate-btn"],
                        size="lg"
                    )
                    
                    # 设置面板
                    settings = create_settings_panel()
                
                # ========== 右侧面板 - 预览和结果 ==========
                with gr.Column(scale=5, min_width=700, elem_classes=["right-column"]):
                    with gr.Tabs(selected='preview_tab') as output_tabs:
                        with gr.Tab('3D 预览', id='preview_tab'):
                            # 使用 HTML 组件 + model-viewer (WebGL) 代替 gr.Model3D (WebGPU)
                            model_viewer_html = gr.HTML(
                                value=MODEL_VIEWER_PLACEHOLDER,
                                label="3D 模型预览",
                                elem_classes=["model-preview"]
                            )
                            with gr.Row():
                                status_text = gr.Markdown(
                                    value="*上传图像并点击生成按钮开始创建 3D 模型*"
                                )
                                # 下载按钮 - 初始禁用，生成完成后启用
                                download_btn = gr.DownloadButton(
                                    label="📥 下载模型",
                                    value=None,
                                    interactive=False,
                                    variant="secondary",
                                    size="sm"
                                )
                        
                        with gr.Tab('生成统计', id='stats_tab'):
                            stats_output = gr.JSON(
                                label="生成统计信息",
                                value={}
                            )
            
            # ========== 事件绑定 ==========
            
            # 刷新状态
            status_components['refresh_btn'].click(
                fn=self.check_health,
                outputs=[
                    status_components['status_indicator'],
                    status_components['health_info']
                ]
            )
            
            # 页面加载时检查状态
            demo.load(
                fn=self.check_health,
                outputs=[
                    status_components['status_indicator'],
                    status_components['health_info']
                ]
            )
            
            # 生成函数
            def do_generate(
                selected_tab,
                single_img, 
                mv_front, mv_back, mv_left, mv_right,
                steps, guidance, octree_res, remove_bg, optimize, max_f, out_fmt,
                # 质量增强选项
                normalize_lighting, lighting_method, lighting_strength,
                fill_holes, make_watertight, smooth_surface, smooth_iterations, recalculate_normals
            ):
                """根据选中的 Tab 判断使用单图还是多视图生成"""
                # 只检查服务是否连通（模型会在第一次请求时懒加载）
                health_response = self.client.health_check()
                if not health_response.success:
                    return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), f"❌ *服务未连接: {health_response.error}*", {"错误": health_response.error}
                
                # 根据选中的 Tab 决定使用哪个接口
                # selected_tab 是 Tab 的 id，'tab_single' 或 'tab_multi_view'
                if selected_tab == 'tab_multi_view':
                    return self._generate_multi_view(
                        mv_front, mv_back, mv_left, mv_right,
                        steps, guidance, octree_res, remove_bg, optimize, max_f, out_fmt,
                        normalize_lighting, lighting_method, lighting_strength,
                        fill_holes, make_watertight, smooth_surface, smooth_iterations, recalculate_normals
                    )
                return self._generate_single(
                    single_img,
                    steps, guidance, octree_res, remove_bg, optimize, max_f, out_fmt,
                    fill_holes, make_watertight, smooth_surface, smooth_iterations, recalculate_normals
                )
            
            # 生成按钮事件
            generate_btn.click(
                fn=lambda: (MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), "⏳ *正在生成 3D 模型，请稍候...*", {}),
                outputs=[model_viewer_html, download_btn, status_text, stats_output]
            ).then(
                fn=do_generate,
                inputs=[
                    input_tabs,
                    single_image,
                    mv_images['front'],
                    mv_images['back'],
                    mv_images['left'],
                    mv_images['right'],
                    settings['num_inference_steps'],
                    settings['guidance_scale'],
                    settings['octree_resolution'],
                    settings['remove_background'],
                    settings['optimize_mesh'],
                    settings['max_faces'],
                    settings['output_format'],
                    # 质量增强选项
                    settings['normalize_lighting'],
                    settings['lighting_method'],
                    settings['lighting_strength'],
                    settings['fill_holes'],
                    settings['make_watertight'],
                    settings['smooth_surface'],
                    settings['smooth_iterations'],
                    settings['recalculate_normals']
                ],
                outputs=[model_viewer_html, download_btn, status_text, stats_output]
            )
        
        return demo
    
    def _generate_single(
        self,
        image: Optional[Image.Image],
        num_inference_steps: int,
        guidance_scale: float,
        octree_resolution: int,
        remove_background: bool,
        optimize_mesh: bool,
        max_faces: int,
        output_format: str,
        # 质量增强选项
        fill_holes: bool = False,
        make_watertight: bool = False,
        smooth_surface: bool = False,
        smooth_iterations: int = 2,
        recalculate_normals: bool = False
    ) -> Tuple[Optional[str], Optional[str], str, Dict]:
        """单图生成"""
        if image is None:
            return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), "❌ *请上传图像*", {"错误": "请上传图像"}
        
        try:
            response = self.client.generate_single(
                image=image,
                num_inference_steps=int(num_inference_steps),
                guidance_scale=float(guidance_scale),
                octree_resolution=int(octree_resolution),
                remove_background=remove_background,
                optimize_mesh=optimize_mesh,
                max_faces=int(max_faces),
                output_format=output_format,
                fill_holes=fill_holes,
                make_watertight=make_watertight,
                smooth_surface=smooth_surface,
                smooth_iterations=int(smooth_iterations),
                recalculate_normals=recalculate_normals
            )
            
            if not response.success:
                return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), f"❌ *生成失败: {response.error}*", {"错误": response.error}
            
            task_id = response.data.get("task_id")
            result_response = self.client.get_task_result(task_id)
            
            if not result_response.success:
                return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), f"❌ *获取结果失败: {result_response.error}*", {"错误": result_response.error}
            
            result_data = result_response.data
            mesh_bytes = base64.b64decode(result_data["mesh_base64"])
            
            # 保存到临时目录用于下载
            download_filename = f"{task_id}.{output_format}"
            download_path = os.path.join(self.temp_dir, download_filename)
            with open(download_path, "wb") as f:
                f.write(mesh_bytes)
            download_path = os.path.abspath(download_path)
            
            # 构建 model-viewer HTML (使用 data URL 方式嵌入模型)
            # 这种方式最可靠，不依赖文件服务配置
            mesh_base64 = result_data["mesh_base64"]
            model_data_url = f"data:model/gltf-binary;base64,{mesh_base64}"
            viewer_html = self._build_model_viewer_html(model_data_url)
            
            stats = {
                "任务 ID": task_id,
                "处理时间": f"{result_data.get('processing_time', 0):.2f} 秒",
                "输入模式": result_data.get("input_mode", "single"),
                "输出格式": result_data.get("format", output_format),
                "文件大小": f"{len(mesh_bytes) / 1024:.1f} KB"
            }
            
            # 返回下载按钮更新：设置文件路径并启用
            return viewer_html, gr.update(value=download_path, interactive=True), "✅ *生成完成！可以在上方预览和下载模型*", stats
            
        except Exception as e:
            return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), f"❌ *发生错误: {str(e)}*", {"错误": str(e)}
    
    def _generate_multi_view(
        self,
        front_image: Optional[Image.Image],
        back_image: Optional[Image.Image],
        left_image: Optional[Image.Image],
        right_image: Optional[Image.Image],
        num_inference_steps: int,
        guidance_scale: float,
        octree_resolution: int,
        remove_background: bool,
        optimize_mesh: bool,
        max_faces: int,
        output_format: str,
        # 质量增强选项
        normalize_lighting: bool = False,
        lighting_method: str = "histogram_matching",
        lighting_strength: float = 0.8,
        fill_holes: bool = False,
        make_watertight: bool = False,
        smooth_surface: bool = False,
        smooth_iterations: int = 2,
        recalculate_normals: bool = False
    ) -> Tuple[Optional[str], Optional[str], str, Dict]:
        """多视图生成"""
        if front_image is None:
            return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), "❌ *请至少上传正面视图图像*", {"错误": "请至少上传正面视图图像"}
        
        views = {"front": front_image}
        if back_image is not None:
            views["back"] = back_image
        if left_image is not None:
            views["left"] = left_image
        if right_image is not None:
            views["right"] = right_image
        
        try:
            response = self.client.generate_multi_view(
                views=views,
                num_inference_steps=int(num_inference_steps),
                guidance_scale=float(guidance_scale),
                octree_resolution=int(octree_resolution),
                remove_background=remove_background,
                optimize_mesh=optimize_mesh,
                max_faces=int(max_faces),
                output_format=output_format,
                normalize_lighting=normalize_lighting,
                lighting_method=lighting_method,
                lighting_strength=float(lighting_strength),
                fill_holes=fill_holes,
                make_watertight=make_watertight,
                smooth_surface=smooth_surface,
                smooth_iterations=int(smooth_iterations),
                recalculate_normals=recalculate_normals
            )
            
            if not response.success:
                return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), f"❌ *生成失败: {response.error}*", {"错误": response.error}
            
            task_id = response.data.get("task_id")
            result_response = self.client.get_task_result(task_id)
            
            if not result_response.success:
                return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), f"❌ *获取结果失败: {result_response.error}*", {"错误": result_response.error}
            
            result_data = result_response.data
            mesh_bytes = base64.b64decode(result_data["mesh_base64"])
            
            # 保存到临时目录用于下载
            download_filename = f"{task_id}.{output_format}"
            download_path = os.path.join(self.temp_dir, download_filename)
            with open(download_path, "wb") as f:
                f.write(mesh_bytes)
            download_path = os.path.abspath(download_path)
            
            # 构建 model-viewer HTML (使用 data URL 方式嵌入模型)
            mesh_base64 = result_data["mesh_base64"]
            model_data_url = f"data:model/gltf-binary;base64,{mesh_base64}"
            viewer_html = self._build_model_viewer_html(model_data_url)
            
            stats = {
                "任务 ID": task_id,
                "处理时间": f"{result_data.get('processing_time', 0):.2f} 秒",
                "输入模式": "multi_view",
                "视图数量": result_data.get("view_count", len(views)),
                "输出格式": result_data.get("format", output_format),
                "文件大小": f"{len(mesh_bytes) / 1024:.1f} KB"
            }
            
            # 返回下载按钮更新：设置文件路径并启用
            return viewer_html, gr.update(value=download_path, interactive=True), "✅ *生成完成！可以在上方预览和下载模型*", stats
            
        except Exception as e:
            return MODEL_VIEWER_PLACEHOLDER, gr.update(value=None, interactive=False), f"❌ *发生错误: {str(e)}*", {"错误": str(e)}


def create_app(
    api_url: str = "http://localhost:8000",
    start_backend: bool = False,
    weights_dir: str = "weights"
) -> gr.Blocks:
    """创建 Gradio 应用"""
    app = GradioApp(
        api_url=api_url,
        start_backend=start_backend,
        weights_dir=weights_dir
    )
    
    if start_backend:
        app._start_backend_server()
    
    return app.build_interface()


def launch_app(
    api_url: str = "http://localhost:8000",
    start_backend: bool = False,
    weights_dir: str = "weights",
    host: str = "0.0.0.0",
    port: int = 7860,
    share: bool = False
):
    """启动 Gradio 应用"""
    app_instance = GradioApp(
        api_url=api_url,
        start_backend=start_backend,
        weights_dir=weights_dir
    )
    
    if start_backend:
        app_instance._start_backend_server()
    
    demo = app_instance.build_interface()
    
    demo.launch(
        server_name=host,
        server_port=port,
        share=share,
        show_error=True,
        theme=gr.themes.Base(),
        css=CUSTOM_CSS,
        allowed_paths=[app_instance.temp_dir]
    )
