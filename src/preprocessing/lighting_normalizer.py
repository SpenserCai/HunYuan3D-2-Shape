# -*- coding: utf-8 -*-
"""
多视图光照一致性校正器
用于统一多视图图像的光照条件
"""

import numpy as np
from PIL import Image
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

from .base import BasePreprocessor


class LightingNormalizer(BasePreprocessor):
    """多视图光照一致性校正器"""
    
    def __init__(
        self,
        reference_view: str = "front",
        method: str = "histogram_matching",
        strength: float = 0.8
    ):
        """
        初始化光照校正器
        
        Args:
            reference_view: 参考视图名称，其他视图将匹配此视图的光照
            method: 校正方法 ("histogram_matching", "color_transfer", "auto_exposure")
            strength: 校正强度 (0.0-1.0)，1.0 表示完全匹配
        """
        self.reference_view = reference_view
        self.method = method
        self.strength = max(0.0, min(1.0, strength))
    
    def process(
        self,
        image: Union[Image.Image, Dict[str, Image.Image]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理图像或多视图图像
        
        Args:
            image: 单张图像或多视图字典
            
        Returns:
            处理结果字典
        """
        if isinstance(image, dict):
            return self._process_multi_view(image, **kwargs)
        else:
            return self._process_single(image, **kwargs)
    
    def _process_single(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """处理单张图像（自动曝光校正）"""
        corrected = self._auto_exposure_correction(image)
        
        # 根据强度混合原图和校正后的图像
        if self.strength < 1.0:
            corrected = self._blend_images(image, corrected, self.strength)
        
        return {
            "image": corrected,
            "correction_applied": True,
            "method": "auto_exposure"
        }
    
    def _process_multi_view(
        self,
        views: Dict[str, Image.Image],
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理多视图图像
        
        Args:
            views: 视图字典 {view_name: image}
            
        Returns:
            处理后的多视图数据
        """
        if self.reference_view not in views:
            # 如果参考视图不存在，使用第一个视图
            self.reference_view = list(views.keys())[0]
        
        reference_image = views[self.reference_view]
        corrected_views = {}
        
        for view_name, image in views.items():
            if view_name == self.reference_view:
                corrected_views[view_name] = image
            else:
                if self.method == "histogram_matching":
                    corrected = self._histogram_matching(image, reference_image)
                elif self.method == "color_transfer":
                    corrected = self._color_transfer(image, reference_image)
                else:
                    corrected = self._auto_exposure_correction(image)
                
                # 根据强度混合
                if self.strength < 1.0:
                    corrected = self._blend_images(image, corrected, self.strength)
                
                corrected_views[view_name] = corrected
        
        return {
            "views": corrected_views,
            "reference_view": self.reference_view,
            "method": self.method,
            "strength": self.strength
        }
    
    def _histogram_matching(
        self,
        source: Image.Image,
        reference: Image.Image
    ) -> Image.Image:
        """
        直方图匹配
        
        Args:
            source: 源图像
            reference: 参考图像
            
        Returns:
            匹配后的图像
        """
        # 转换为 numpy 数组
        src_array = np.array(source.convert("RGB")).astype(np.float32)
        ref_array = np.array(reference.convert("RGB")).astype(np.float32)
        
        result = np.zeros_like(src_array)
        
        # 对每个通道进行直方图匹配
        for channel in range(3):
            src_channel = src_array[:, :, channel].flatten()
            ref_channel = ref_array[:, :, channel].flatten()
            
            # 计算累积分布函数
            src_hist, src_bins = np.histogram(src_channel, bins=256, range=(0, 256))
            ref_hist, ref_bins = np.histogram(ref_channel, bins=256, range=(0, 256))
            
            src_cdf = np.cumsum(src_hist).astype(np.float32)
            src_cdf = src_cdf / src_cdf[-1]
            
            ref_cdf = np.cumsum(ref_hist).astype(np.float32)
            ref_cdf = ref_cdf / ref_cdf[-1]
            
            # 创建查找表
            lookup_table = np.zeros(256)
            ref_idx = 0
            for src_idx in range(256):
                while ref_idx < 255 and ref_cdf[ref_idx] < src_cdf[src_idx]:
                    ref_idx += 1
                lookup_table[src_idx] = ref_idx
            
            # 应用查找表
            result_channel = lookup_table[src_array[:, :, channel].astype(np.uint8)]
            result[:, :, channel] = result_channel
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # 保留原始 alpha 通道
        if source.mode == "RGBA":
            result_image = Image.fromarray(result, mode="RGB")
            result_image = result_image.convert("RGBA")
            result_image.putalpha(source.split()[3])
            return result_image
        
        return Image.fromarray(result, mode="RGB")
    
    def _color_transfer(
        self,
        source: Image.Image,
        reference: Image.Image
    ) -> Image.Image:
        """
        颜色转移（基于 LAB 色彩空间）
        
        Args:
            source: 源图像
            reference: 参考图像
            
        Returns:
            转移后的图像
        """
        import cv2
        
        # 转换为 numpy 数组
        src_array = np.array(source.convert("RGB"))
        ref_array = np.array(reference.convert("RGB"))
        
        # 转换到 LAB 色彩空间
        src_lab = cv2.cvtColor(src_array, cv2.COLOR_RGB2LAB).astype(np.float32)
        ref_lab = cv2.cvtColor(ref_array, cv2.COLOR_RGB2LAB).astype(np.float32)
        
        # 计算均值和标准差
        src_mean, src_std = cv2.meanStdDev(src_lab)
        ref_mean, ref_std = cv2.meanStdDev(ref_lab)
        
        src_mean = src_mean.flatten()
        src_std = src_std.flatten()
        ref_mean = ref_mean.flatten()
        ref_std = ref_std.flatten()
        
        # 避免除零
        src_std = np.where(src_std == 0, 1, src_std)
        
        # 应用颜色转移
        result_lab = src_lab.copy()
        for i in range(3):
            result_lab[:, :, i] = (src_lab[:, :, i] - src_mean[i]) * (ref_std[i] / src_std[i]) + ref_mean[i]
        
        # 裁剪到有效范围
        result_lab[:, :, 0] = np.clip(result_lab[:, :, 0], 0, 255)
        result_lab[:, :, 1] = np.clip(result_lab[:, :, 1], 0, 255)
        result_lab[:, :, 2] = np.clip(result_lab[:, :, 2], 0, 255)
        
        # 转回 RGB
        result = cv2.cvtColor(result_lab.astype(np.uint8), cv2.COLOR_LAB2RGB)
        
        # 保留原始 alpha 通道
        if source.mode == "RGBA":
            result_image = Image.fromarray(result, mode="RGB")
            result_image = result_image.convert("RGBA")
            result_image.putalpha(source.split()[3])
            return result_image
        
        return Image.fromarray(result, mode="RGB")
    
    def _auto_exposure_correction(self, image: Image.Image) -> Image.Image:
        """
        自动曝光校正
        
        Args:
            image: 输入图像
            
        Returns:
            校正后的图像
        """
        import cv2
        
        # 转换为 numpy 数组
        img_array = np.array(image.convert("RGB"))
        
        # 转换到 LAB 色彩空间
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        
        # 对 L 通道应用 CLAHE（对比度受限自适应直方图均衡化）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # 转回 RGB
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # 保留原始 alpha 通道
        if image.mode == "RGBA":
            result_image = Image.fromarray(result, mode="RGB")
            result_image = result_image.convert("RGBA")
            result_image.putalpha(image.split()[3])
            return result_image
        
        return Image.fromarray(result, mode="RGB")
    
    def _blend_images(
        self,
        original: Image.Image,
        corrected: Image.Image,
        strength: float
    ) -> Image.Image:
        """
        混合原图和校正后的图像
        
        Args:
            original: 原始图像
            corrected: 校正后的图像
            strength: 混合强度
            
        Returns:
            混合后的图像
        """
        return Image.blend(original.convert("RGBA"), corrected.convert("RGBA"), strength)
