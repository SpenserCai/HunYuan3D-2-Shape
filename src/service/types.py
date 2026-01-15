# -*- coding: utf-8 -*-
"""
服务层类型定义
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any
from enum import Enum


class ModelType(Enum):
    """模型类型枚举"""
    HUNYUAN3D_2_1 = "hunyuan3d-2.1"
    HUNYUAN3D_2MV = "hunyuan3d-2mv"


@dataclass
class GenerationConfig:
    """生成配置"""
    num_inference_steps: int = 50
    guidance_scale: float = 5.0
    octree_resolution: int = 384
    remove_background: bool = True
    optimize_mesh: bool = True
    max_faces: int = 40000
    output_format: str = "glb"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class GenerationResult:
    """生成结果"""
    mesh: Any  # trimesh.Trimesh
    task_id: str
    processing_time: float
    config: GenerationConfig


@dataclass
class ServiceStatus:
    """服务状态"""
    is_ready: bool
    loaded_models: List[str]
    gpu_memory_used: float
    gpu_memory_total: float
