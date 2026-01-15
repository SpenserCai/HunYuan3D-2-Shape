# -*- coding: utf-8 -*-
"""
基于 BiRefNet 的背景移除器
"""

import torch
from PIL import Image
from torchvision import transforms
from typing import Dict, Any, Optional

from .base import BasePreprocessor


def get_default_device() -> str:
    """自动检测最佳设备"""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


class BiRefNetBackgroundRemover(BasePreprocessor):
    """基于 BiRefNet 的背景移除器"""
    
    def __init__(
        self,
        model_path: str = "weights/BiRefNet",
        device: Optional[str] = None,
        image_size: int = 1024
    ):
        """
        初始化背景移除器
        
        Args:
            model_path: BiRefNet 模型路径
            device: 推理设备，None 时自动检测
            image_size: 处理图像尺寸
        """
        self.device = device or get_default_device()
        self.image_size = image_size
        self.model_path = model_path
        self._model = None
        self._transform = None
    
    @property
    def model(self):
        """延迟加载模型"""
        if self._model is None:
            self._model = self._load_model(self.model_path)
        return self._model
    
    @property
    def transform(self):
        """延迟创建变换"""
        if self._transform is None:
            self._transform = self._create_transform()
        return self._transform
    
    def _load_model(self, model_path: str):
        """加载 BiRefNet 模型"""
        from transformers import AutoModelForImageSegmentation
        
        model = AutoModelForImageSegmentation.from_pretrained(
            model_path, trust_remote_code=True
        )
        
        if self.device == "cuda":
            torch.set_float32_matmul_precision('high')
        
        model.to(self.device)
        model.eval()
        return model
    
    def _create_transform(self):
        """创建图像预处理变换"""
        return transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def process(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """
        移除背景，返回RGBA图像
        
        Args:
            image: 输入图像
            
        Returns:
            包含处理结果的字典:
            - image: RGBA 图像（背景已移除）
            - mask: 分割掩码
            - original_size: 原始尺寸
        """
        original_size = image.size
        rgb_image = image.convert("RGB")
        
        # 预处理
        input_tensor = self.transform(rgb_image).unsqueeze(0).to(self.device)
        
        # 推理
        with torch.no_grad():
            pred = self.model(input_tensor)[-1].sigmoid()
        
        # 后处理
        pred = pred.cpu().squeeze()
        mask = transforms.ToPILImage()(pred).resize(original_size)
        
        # 应用透明度
        result = rgb_image.copy()
        result.putalpha(mask)
        
        return {
            "image": result,
            "mask": mask,
            "original_size": original_size
        }
    
    def unload(self):
        """卸载模型释放显存"""
        if self._model is not None:
            del self._model
            self._model = None
            if self.device == "cuda":
                torch.cuda.empty_cache()
            elif self.device == "mps":
                torch.mps.empty_cache()
