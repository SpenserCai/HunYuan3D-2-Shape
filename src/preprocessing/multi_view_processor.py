# -*- coding: utf-8 -*-
"""
多视图预处理器
支持处理多个视角的图像输入
"""

from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from PIL import Image

from .base import BasePreprocessor
from .background_remover import BiRefNetBackgroundRemover


# 视角顺序
VIEW_ORDER = ['front', 'left', 'back', 'right']


class MultiViewProcessor(BasePreprocessor):
    """多视图预处理器"""
    
    def __init__(
        self,
        background_remover: Optional[BiRefNetBackgroundRemover] = None,
        image_size: int = 512
    ):
        """
        初始化多视图预处理器
        
        Args:
            background_remover: 背景移除器实例（可选）
            image_size: 处理后的图像尺寸
        """
        self.background_remover = background_remover
        self.image_size = image_size
    
    def process(
        self,
        images: Dict[str, Union[str, Path, Image.Image]],
        remove_background: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理多视图图像
        
        Args:
            images: 视图字典 {view_name: image}
                   view_name: 'front', 'left', 'back', 'right'
                   image: 文件路径或 PIL.Image
            remove_background: 是否移除背景
            
        Returns:
            处理后的多视图数据:
            - views: 处理后的图像字典
            - masks: 掩码字典
            - view_count: 视图数量
            - available_views: 可用视图列表
        """
        processed_views = {}
        masks = {}
        
        for view_name, image in images.items():
            # 验证视角名称
            if view_name not in VIEW_ORDER:
                raise ValueError(f"Invalid view name: {view_name}. Must be one of {VIEW_ORDER}")
            
            # 加载图像
            if isinstance(image, (str, Path)):
                image = Image.open(image)
            
            # 确保是 PIL Image
            if not isinstance(image, Image.Image):
                raise TypeError(f"Expected PIL.Image, got {type(image)}")
            
            # 背景移除
            if remove_background and self.background_remover is not None:
                result = self.background_remover.process(image)
                processed_views[view_name] = result["image"]
                masks[view_name] = result["mask"]
            else:
                # 转换为 RGBA
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                processed_views[view_name] = image
                masks[view_name] = None
        
        return {
            "views": processed_views,
            "masks": masks,
            "view_count": len(processed_views),
            "available_views": list(processed_views.keys())
        }
    
    def validate_views(self, images: Dict[str, Any]) -> bool:
        """
        验证视图输入
        
        Args:
            images: 视图字典
            
        Returns:
            是否有效（至少需要正面视图）
        """
        return 'front' in images
    
    def get_sorted_views(
        self,
        views: Dict[str, Image.Image]
    ) -> List[tuple]:
        """
        按标准顺序返回视图
        
        Args:
            views: 视图字典
            
        Returns:
            排序后的 (view_name, image) 列表
        """
        view_order_map = {v: i for i, v in enumerate(VIEW_ORDER)}
        sorted_items = sorted(
            views.items(),
            key=lambda x: view_order_map.get(x[0], 99)
        )
        return sorted_items
