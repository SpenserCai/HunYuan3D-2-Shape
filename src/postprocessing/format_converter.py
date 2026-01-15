# -*- coding: utf-8 -*-
"""
格式转换器
"""

import trimesh
from pathlib import Path
from typing import Union, List

from .base import BasePostprocessor


class FormatConverter(BasePostprocessor):
    """格式转换器"""
    
    SUPPORTED_FORMATS: List[str] = ['glb', 'gltf', 'obj', 'ply', 'stl', 'off']
    
    def process(self, mesh: trimesh.Trimesh, **kwargs) -> trimesh.Trimesh:
        """
        格式转换在导出时处理，这里只做验证
        
        Args:
            mesh: 输入 Mesh
            
        Returns:
            原始 Mesh
        """
        return mesh
    
    def export(
        self,
        mesh: trimesh.Trimesh,
        output_path: Union[str, Path],
        format: str = None
    ) -> str:
        """
        导出 Mesh 到指定格式
        
        Args:
            mesh: 要导出的 Mesh
            output_path: 输出路径
            format: 输出格式，None 时从路径推断
            
        Returns:
            输出文件路径
            
        Raises:
            ValueError: 不支持的格式
        """
        output_path = Path(output_path)
        
        if format is None:
            format = output_path.suffix.lstrip('.')
        
        format = format.lower()
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 导出
        mesh.export(str(output_path), file_type=format)
        return str(output_path)
    
    def to_bytes(self, mesh: trimesh.Trimesh, format: str = 'glb') -> bytes:
        """
        将 Mesh 转换为字节
        
        Args:
            mesh: 要转换的 Mesh
            format: 输出格式
            
        Returns:
            Mesh 的字节表示
        """
        format = format.lower()
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")
        
        return mesh.export(file_type=format)
