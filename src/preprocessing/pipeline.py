# -*- coding: utf-8 -*-
"""
预处理管线
"""

from typing import List, Dict, Any
from PIL import Image

from .base import BasePreprocessor


class PreprocessingPipeline:
    """预处理管线，串联多个预处理器"""
    
    def __init__(self, processors: List[BasePreprocessor] = None):
        """
        初始化预处理管线
        
        Args:
            processors: 预处理器列表
        """
        self.processors = processors or []
    
    def add(self, processor: BasePreprocessor) -> 'PreprocessingPipeline':
        """
        添加预处理器
        
        Args:
            processor: 预处理器实例
            
        Returns:
            self，支持链式调用
        """
        self.processors.append(processor)
        return self
    
    def process(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """
        执行预处理管线
        
        Args:
            image: 输入图像
            **kwargs: 额外参数
            
        Returns:
            最终处理结果
        """
        result = {"image": image}
        for processor in self.processors:
            result = processor.process(result["image"], **kwargs)
        return result
    
    def __call__(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        return self.process(image, **kwargs)
    
    def __len__(self) -> int:
        return len(self.processors)
