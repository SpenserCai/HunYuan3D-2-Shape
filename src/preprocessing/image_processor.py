# -*- coding: utf-8 -*-
"""
图像预处理增强器
"""

from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any, Optional

from .base import BasePreprocessor


class ImageEnhancer(BasePreprocessor):
    """图像增强预处理器"""
    
    def __init__(
        self,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        denoise: bool = False
    ):
        """
        初始化图像增强器
        
        Args:
            brightness: 亮度调整因子 (1.0 = 原始)
            contrast: 对比度调整因子 (1.0 = 原始)
            sharpness: 锐度调整因子 (1.0 = 原始)
            denoise: 是否进行降噪
        """
        self.brightness = brightness
        self.contrast = contrast
        self.sharpness = sharpness
        self.denoise = denoise
    
    def process(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """
        增强图像
        
        Args:
            image: 输入图像
            
        Returns:
            包含处理结果的字典
        """
        result = image.copy()
        
        # 亮度调整
        if self.brightness != 1.0:
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(self.brightness)
        
        # 对比度调整
        if self.contrast != 1.0:
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(self.contrast)
        
        # 锐度调整
        if self.sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(result)
            result = enhancer.enhance(self.sharpness)
        
        # 降噪
        if self.denoise:
            # 使用中值滤波进行简单降噪
            result = result.filter(ImageFilter.MedianFilter(size=3))
        
        return {
            "image": result,
            "original_size": image.size
        }
