# -*- coding: utf-8 -*-
"""
高级 Mesh 优化器
包含孔洞填充、水密网格生成、表面平滑等功能
"""

import tempfile
from typing import Optional

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


class AdvancedMeshOptimizer(BasePostprocessor):
    """
    高级 Mesh 优化器
    
    提供以下功能：
    - 孔洞填充
    - 水密网格生成
    - 表面平滑
    - 法线重计算
    """
    
    def __init__(
        self,
        fill_holes: bool = True,
        max_hole_size: int = 100,
        make_watertight: bool = True,
        smooth_surface: bool = True,
        smooth_iterations: int = 2,
        smooth_lambda: float = 0.5,
        recalculate_normals: bool = True
    ):
        """
        初始化高级 Mesh 优化器
        
        Args:
            fill_holes: 是否填充孔洞
            max_hole_size: 最大孔洞大小（边数）
            make_watertight: 是否生成水密网格
            smooth_surface: 是否平滑表面
            smooth_iterations: 平滑迭代次数
            smooth_lambda: 平滑强度 (0.0-1.0)
            recalculate_normals: 是否重新计算法线
        """
        self.fill_holes = fill_holes
        self.max_hole_size = max_hole_size
        self.make_watertight = make_watertight
        self.smooth_surface = smooth_surface
        self.smooth_iterations = smooth_iterations
        self.smooth_lambda = smooth_lambda
        self.recalculate_normals = recalculate_normals
    
    def _fill_holes(self, ms: pymeshlab.MeshSet) -> pymeshlab.MeshSet:
        """
        填充网格孔洞
        
        Args:
            ms: PyMeshLab MeshSet
            
        Returns:
            处理后的 MeshSet
        """
        try:
            ms.apply_filter(
                "meshing_close_holes",
                maxholesize=self.max_hole_size,
                newfaceselected=False
            )
        except Exception as e:
            # 某些网格可能没有孔洞或无法填充
            print(f"Warning: Hole filling failed: {e}")
        return ms
    
    def _make_watertight(self, ms: pymeshlab.MeshSet) -> pymeshlab.MeshSet:
        """
        生成水密网格
        
        修复非流形边和顶点，确保网格是封闭的
        
        Args:
            ms: PyMeshLab MeshSet
            
        Returns:
            处理后的 MeshSet
        """
        try:
            # 修复非流形边
            ms.apply_filter("meshing_repair_non_manifold_edges")
        except Exception as e:
            print(f"Warning: Non-manifold edge repair failed: {e}")
        
        try:
            # 修复非流形顶点
            ms.apply_filter("meshing_repair_non_manifold_vertices")
        except Exception as e:
            print(f"Warning: Non-manifold vertex repair failed: {e}")
        
        try:
            # 移除重复面
            ms.apply_filter("meshing_remove_duplicate_faces")
        except Exception as e:
            print(f"Warning: Duplicate face removal failed: {e}")
        
        try:
            # 移除重复顶点
            ms.apply_filter("meshing_remove_duplicate_vertices")
        except Exception as e:
            print(f"Warning: Duplicate vertex removal failed: {e}")
        
        try:
            # 移除零面积面
            ms.apply_filter("meshing_remove_null_faces")
        except Exception as e:
            print(f"Warning: Null face removal failed: {e}")
        
        return ms
    
    def _smooth_surface(self, ms: pymeshlab.MeshSet) -> pymeshlab.MeshSet:
        """
        平滑表面
        
        使用 Taubin 平滑算法，可以平滑表面同时保持体积
        
        Args:
            ms: PyMeshLab MeshSet
            
        Returns:
            处理后的 MeshSet
        """
        try:
            # Taubin 平滑 - 比 Laplacian 平滑更好地保持体积
            ms.apply_filter(
                "apply_coord_taubin_smoothing",
                stepsmoothnum=self.smooth_iterations,
                lambda_=self.smooth_lambda,
                mu=-0.53  # 标准 Taubin 参数
            )
        except Exception as e:
            print(f"Warning: Taubin smoothing failed, trying Laplacian: {e}")
            try:
                # 回退到 Laplacian 平滑
                ms.apply_filter(
                    "apply_coord_laplacian_smoothing",
                    stepsmoothnum=self.smooth_iterations,
                    cotangentweight=True
                )
            except Exception as e2:
                print(f"Warning: Laplacian smoothing also failed: {e2}")
        
        return ms
    
    def _recalculate_normals(self, ms: pymeshlab.MeshSet) -> pymeshlab.MeshSet:
        """
        重新计算法线
        
        Args:
            ms: PyMeshLab MeshSet
            
        Returns:
            处理后的 MeshSet
        """
        try:
            # 重新计算面法线
            ms.apply_filter("compute_normal_per_face")
        except Exception as e:
            print(f"Warning: Face normal computation failed: {e}")
        
        try:
            # 重新计算顶点法线
            ms.apply_filter("compute_normal_per_vertex")
        except Exception as e:
            print(f"Warning: Vertex normal computation failed: {e}")
        
        try:
            # 统一法线方向
            ms.apply_filter("meshing_re_orient_faces_coherentely")
        except Exception as e:
            print(f"Warning: Face reorientation failed: {e}")
        
        return ms
    
    def process(self, mesh: trimesh.Trimesh, **kwargs) -> trimesh.Trimesh:
        """
        执行高级网格优化
        
        Args:
            mesh: 输入 Mesh
            **kwargs: 可覆盖默认参数
                - fill_holes: bool
                - make_watertight: bool
                - smooth_surface: bool
                - smooth_iterations: int
                - recalculate_normals: bool
            
        Returns:
            优化后的 Mesh
        """
        # 获取参数（支持运行时覆盖）
        fill_holes = kwargs.get('fill_holes', self.fill_holes)
        make_watertight = kwargs.get('make_watertight', self.make_watertight)
        smooth_surface = kwargs.get('smooth_surface', self.smooth_surface)
        smooth_iterations = kwargs.get('smooth_iterations', self.smooth_iterations)
        recalculate_normals = kwargs.get('recalculate_normals', self.recalculate_normals)
        
        # 转换为 pymeshlab
        ms = trimesh2pymeshlab(mesh)
        
        # 按顺序应用优化
        # 1. 首先修复基本问题（水密性）
        if make_watertight:
            ms = self._make_watertight(ms)
        
        # 2. 填充孔洞
        if fill_holes:
            ms = self._fill_holes(ms)
        
        # 3. 平滑表面
        if smooth_surface:
            self.smooth_iterations = smooth_iterations
            ms = self._smooth_surface(ms)
        
        # 4. 重新计算法线
        if recalculate_normals:
            ms = self._recalculate_normals(ms)
        
        # 转回 trimesh
        return pymeshlab2trimesh(ms)
    
    def get_mesh_stats(self, mesh: trimesh.Trimesh) -> dict:
        """
        获取网格统计信息
        
        Args:
            mesh: 输入 Mesh
            
        Returns:
            统计信息字典
        """
        return {
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
            "is_watertight": mesh.is_watertight,
            "is_winding_consistent": mesh.is_winding_consistent,
            "euler_number": mesh.euler_number,
            "bounds": mesh.bounds.tolist() if mesh.bounds is not None else None
        }
