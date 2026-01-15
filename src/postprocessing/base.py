# -*- coding: utf-8 -*-
"""
后处理器基类
"""

from abc import ABC, abstractmethod
from typing import Union
import trimesh


class BasePostprocessor(ABC):
    """后处理器基类"""
    
    @abstractmethod
    def process(self, mesh: trimesh.Trimesh, **kwargs) -> trimesh.Trimesh:
        """
        处理 Mesh，返回处理后的 Mesh
        
        Args:
            mesh: trimesh.Trimesh 对象
            **kwargs: 额外参数
            
        Returns:
            处理后的 trimesh.Trimesh 对象
        """
        pass
    
    def __call__(self, mesh: trimesh.Trimesh, **kwargs) -> trimesh.Trimesh:
        return self.process(mesh, **kwargs)
