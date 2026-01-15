# -*- coding: utf-8 -*-
"""
Mesh 优化器
整合官方后处理功能
"""

import tempfile
from typing import Union, Optional

import numpy as np
import pymeshlab
import trimesh

from .base import BasePostprocessor


def trimesh2pymeshlab(mesh: trimesh.Trimesh) -> pymeshlab.MeshSet:
    """将 trimesh 转换为 pymeshlab"""
    with tempfile.NamedTemporaryFile(suffix='.ply', delete=False) as temp_file:
        if isinstance(mesh, trimesh.scene.Scene):
            combined = trimesh.Trimesh()
            for geom in mesh.geometry.values():
                combined = trimesh.util.concatenate([combined, geom])
            mesh = combined
        mesh.export(temp_file.name)
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(temp_file.name)
    return ms


def pymeshlab2trimesh(mesh: pymeshlab.MeshSet) -> trimesh.Trimesh:
    """将 pymeshlab 转换为 trimesh"""
    with tempfile.NamedTemporaryFile(suffix='.ply', delete=False) as temp_file:
        mesh.save_current_mesh(temp_file.name)
        result = trimesh.load(temp_file.name)
    
    if isinstance(result, trimesh.Scene):
        combined = trimesh.Trimesh()
        for geom in result.geometry.values():
            combined = trimesh.util.concatenate([combined, geom])
        result = combined
    
    return result


class MeshOptimizer(BasePostprocessor):
    """Mesh 优化器，整合官方后处理功能"""
    
    def __init__(
        self,
        reduce_faces: bool = True,
        max_faces: int = 40000,
        remove_floaters: bool = True,
        remove_degenerate: bool = True
    ):
        """
        初始化 Mesh 优化器
        
        Args:
            reduce_faces: 是否减少面数
            max_faces: 最大面数
            remove_floaters: 是否移除浮点
            remove_degenerate: 是否移除退化面
        """
        self.reduce_faces = reduce_faces
        self.max_faces = max_faces
        self.remove_floaters = remove_floaters
        self.remove_degenerate = remove_degenerate
    
    def _reduce_faces(self, ms: pymeshlab.MeshSet, max_facenum: int) -> pymeshlab.MeshSet:
        """减少面数"""
        if max_facenum > ms.current_mesh().face_number():
            return ms
        
        ms.apply_filter(
            "meshing_decimation_quadric_edge_collapse",
            targetfacenum=max_facenum,
            qualitythr=1.0,
            preserveboundary=True,
            boundaryweight=3,
            preservenormal=True,
            preservetopology=True,
            autoclean=True
        )
        return ms
    
    def _remove_floaters(self, ms: pymeshlab.MeshSet) -> pymeshlab.MeshSet:
        """移除浮点"""
        ms.apply_filter(
            "compute_selection_by_small_disconnected_components_per_face",
            nbfaceratio=0.005
        )
        ms.apply_filter("compute_selection_transfer_face_to_vertex", inclusive=False)
        ms.apply_filter("meshing_remove_selected_vertices_and_faces")
        return ms
    
    def _remove_degenerate(self, ms: pymeshlab.MeshSet) -> pymeshlab.MeshSet:
        """移除退化面"""
        with tempfile.NamedTemporaryFile(suffix='.ply', delete=False) as temp_file:
            ms.save_current_mesh(temp_file.name)
            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(temp_file.name)
        return ms
    
    def process(self, mesh: trimesh.Trimesh, **kwargs) -> trimesh.Trimesh:
        """
        优化 Mesh
        
        Args:
            mesh: 输入 Mesh
            **kwargs: 可覆盖默认参数
            
        Returns:
            优化后的 Mesh
        """
        max_faces = kwargs.get('max_faces', self.max_faces)
        
        # 转换为 pymeshlab
        ms = trimesh2pymeshlab(mesh)
        
        # 应用优化
        if self.remove_floaters:
            ms = self._remove_floaters(ms)
        
        if self.reduce_faces:
            ms = self._reduce_faces(ms, max_faces)
        
        if self.remove_degenerate:
            ms = self._remove_degenerate(ms)
        
        # 转回 trimesh
        return pymeshlab2trimesh(ms)
