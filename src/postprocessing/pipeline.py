# -*- coding: utf-8 -*-
"""
后处理管线
"""

from typing import List
import trimesh

from .base import BasePostprocessor


class PostprocessingPipeline:
    """后处理管线，串联多个后处理器"""
    
    def __init__(self, processors: List[BasePostprocessor] = None):
        """
        初始化后处理管线
        
        Args:
            processors: 后处理器列表
        """
        self.processors = processors or []
    
    def add(self, processor: BasePostprocessor) -> 'PostprocessingPipeline':
        """
        添加后处理器
        
        Args:
            processor: 后处理器实例
            
        Returns:
            self，支持链式调用
        """
        self.processors.append(processor)
        return self
    
    def process(self, mesh: trimesh.Trimesh, **kwargs) -> trimesh.Trimesh:
        """
        执行后处理管线
        
        Args:
            mesh: 输入 Mesh
            **kwargs: 额外参数
            
        Returns:
            处理后的 Mesh
        """
        for processor in self.processors:
            mesh = processor.process(mesh, **kwargs)
        return mesh
    
    def __call__(self, mesh: trimesh.Trimesh, **kwargs) -> trimesh.Trimesh:
        return self.process(mesh, **kwargs)
    
    def __len__(self) -> int:
        return len(self.processors)
