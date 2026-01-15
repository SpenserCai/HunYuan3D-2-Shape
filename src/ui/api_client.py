# -*- coding: utf-8 -*-
"""
API 客户端封装 - 用于 Gradio UI 调用后端 API
"""

import base64
import io
import time
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass

import requests
from PIL import Image


@dataclass
class APIResponse:
    """API 响应封装"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ShapeAPIClient:
    """Shape Generation API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: API 服务器地址
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 300  # 5分钟超时，生成可能需要较长时间
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> APIResponse:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.timeout
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=json_data, timeout=timeout)
            else:
                return APIResponse(success=False, error=f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return APIResponse(success=True, data=response.json())
            else:
                error_detail = response.json().get('detail', response.text)
                return APIResponse(success=False, error=f"HTTP {response.status_code}: {error_detail}")
                
        except requests.exceptions.Timeout:
            return APIResponse(success=False, error="请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            return APIResponse(success=False, error=f"无法连接到服务器 {self.base_url}")
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def health_check(self) -> APIResponse:
        """健康检查"""
        return self._make_request("GET", "/api/v1/health", timeout=10)
    
    def get_models(self) -> APIResponse:
        """获取模型列表"""
        return self._make_request("GET", "/api/v1/models", timeout=10)
    
    def load_model(self, model_id: str) -> APIResponse:
        """加载模型"""
        return self._make_request("POST", f"/api/v1/models/{model_id}/load")
    
    def unload_model(self, model_id: str) -> APIResponse:
        """卸载模型"""
        return self._make_request("POST", f"/api/v1/models/{model_id}/unload")
    
    @staticmethod
    def image_to_base64(image: Image.Image) -> str:
        """将 PIL Image 转换为 Base64 字符串"""
        buffer = io.BytesIO()
        # 保存为 PNG 格式以保留透明度
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    @staticmethod
    def base64_to_bytes(base64_str: str) -> bytes:
        """将 Base64 字符串转换为字节"""
        return base64.b64decode(base64_str)
    
    def generate_single(
        self,
        image: Image.Image,
        num_inference_steps: int = 50,
        guidance_scale: float = 5.0,
        octree_resolution: int = 384,
        remove_background: bool = True,
        optimize_mesh: bool = True,
        max_faces: int = 40000,
        output_format: str = "glb"
    ) -> APIResponse:
        """
        单图生成 3D 模型
        
        Args:
            image: 输入图像
            num_inference_steps: 推理步数
            guidance_scale: 引导强度
            octree_resolution: 八叉树分辨率
            remove_background: 是否移除背景
            optimize_mesh: 是否优化网格
            max_faces: 最大面数
            output_format: 输出格式
            
        Returns:
            API 响应
        """
        image_base64 = self.image_to_base64(image)
        
        payload = {
            "image_base64": image_base64,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "octree_resolution": octree_resolution,
            "remove_background": remove_background,
            "optimize_mesh": optimize_mesh,
            "max_faces": max_faces,
            "output_format": output_format
        }
        
        return self._make_request("POST", "/api/v1/generate", json_data=payload)
    
    def generate_multi_view(
        self,
        views: Dict[str, Image.Image],
        num_inference_steps: int = 50,
        guidance_scale: float = 5.0,
        octree_resolution: int = 384,
        remove_background: bool = True,
        optimize_mesh: bool = True,
        max_faces: int = 40000,
        output_format: str = "glb"
    ) -> APIResponse:
        """
        多视图生成 3D 模型
        
        Args:
            views: 视图字典 {view_name: image}
            其他参数同 generate_single
            
        Returns:
            API 响应
        """
        views_base64 = {
            name: self.image_to_base64(img)
            for name, img in views.items()
        }
        
        payload = {
            "views": views_base64,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "octree_resolution": octree_resolution,
            "remove_background": remove_background,
            "optimize_mesh": optimize_mesh,
            "max_faces": max_faces,
            "output_format": output_format
        }
        
        return self._make_request("POST", "/api/v1/generate/multi-view", json_data=payload)
    
    def get_task_status(self, task_id: str) -> APIResponse:
        """获取任务状态"""
        return self._make_request("GET", f"/api/v1/tasks/{task_id}", timeout=10)
    
    def get_task_result(self, task_id: str) -> APIResponse:
        """获取任务结果"""
        return self._make_request("GET", f"/api/v1/tasks/{task_id}/result")
