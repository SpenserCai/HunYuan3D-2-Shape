# -*- coding: utf-8 -*-
"""
服务层类型定义
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any, Dict, Union
from enum import Enum
from PIL import Image


class ModelType(Enum):
    """模型类型枚举"""
    HUNYUAN3D_2_1 = "hunyuan3d-2.1"
    HUNYUAN3D_2MV = "hunyuan3d-2mv"


class InputMode(Enum):
    """输入模式枚举"""
    SINGLE_IMAGE = "single"      # 单图模式
    MULTI_VIEW = "multi_view"    # 多视图模式


class ViewType(Enum):
    """视角类型枚举"""
    FRONT = "front"
    LEFT = "left"
    BACK = "back"
    RIGHT = "right"


# 视角顺序映射
VIEW_ORDER = {
    ViewType.FRONT.value: 0,
    ViewType.LEFT.value: 1,
    ViewType.BACK.value: 2,
    ViewType.RIGHT.value: 3
}


@dataclass
class MultiViewInput:
    """多视图输入"""
    views: Dict[str, Any]  # {view_name: image} - image can be str path or PIL.Image
    
    def validate(self) -> bool:
        """验证视图完整性（至少需要正面视图）"""
        required = {ViewType.FRONT.value}
        return required.issubset(self.views.keys())
    
    @property
    def view_count(self) -> int:
        """视图数量"""
        return len(self.views)
    
    @property
    def available_views(self) -> List[str]:
        """可用视图列表"""
        return list(self.views.keys())
    
    def get_sorted_views(self) -> List[tuple]:
        """按标准顺序返回视图"""
        sorted_items = sorted(
            self.views.items(),
            key=lambda x: VIEW_ORDER.get(x[0], 99)
        )
        return sorted_items


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
    
    # 多视图相关配置
    input_mode: InputMode = InputMode.SINGLE_IMAGE
    auto_detect_mode: bool = True  # 自动检测输入模式
    
    # 高级预处理选项
    normalize_lighting: bool = False  # 多视图光照一致性校正
    lighting_method: str = "histogram_matching"  # 光照校正方法
    lighting_strength: float = 0.8  # 光照校正强度
    
    # 高级后处理选项
    fill_holes: bool = False  # 填充孔洞
    max_hole_size: int = 100  # 最大孔洞大小
    make_watertight: bool = False  # 生成水密网格
    smooth_surface: bool = False  # 表面平滑
    smooth_iterations: int = 2  # 平滑迭代次数
    recalculate_normals: bool = False  # 重新计算法线
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = asdict(self)
        # 将枚举转换为字符串
        result['input_mode'] = self.input_mode.value
        return result


@dataclass
class GenerationResult:
    """生成结果"""
    mesh: Any  # trimesh.Trimesh
    task_id: str
    processing_time: float
    config: GenerationConfig
    input_mode: InputMode = InputMode.SINGLE_IMAGE
    view_count: int = 1  # 使用的视图数量


@dataclass
class ServiceStatus:
    """服务状态"""
    is_ready: bool
    loaded_models: List[str]
    gpu_memory_used: float
    gpu_memory_total: float
