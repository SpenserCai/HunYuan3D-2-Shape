# -*- coding: utf-8 -*-
"""
预处理器基类
"""

from abc import ABC, abstractmethod
from PIL import Image
from typing import Dict, Any


class BasePreprocessor(ABC):
    """预处理器基类"""
    
    @abstractmethod
    def process(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """
        处理图像，返回处理结果
        
        Args:
            image: PIL Image 对象
            **kwargs: 额外参数
            
        Returns:
            包含处理结果的字典，至少包含 'image' 键
        """
        pass
    
    def __call__(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        return self.process(image, **kwargs)
