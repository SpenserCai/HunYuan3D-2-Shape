# -*- coding: utf-8 -*-
"""
模型生命周期管理器
"""

import os
import torch
from typing import Dict, Optional, List, Any

from .types import ModelType


def get_default_device() -> str:
    """自动检测最佳设备"""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


class ModelManager:
    """模型生命周期管理器"""
    
    def __init__(
        self,
        weights_dir: str = "weights",
        device: Optional[str] = None,
        dtype: torch.dtype = torch.float16
    ):
        """
        初始化模型管理器
        
        Args:
            weights_dir: 模型权重目录
            device: 推理设备，None 时自动检测
            dtype: 模型数据类型
        """
        self.weights_dir = weights_dir
        self._device = device or get_default_device()
        self._dtype = dtype
        self._models: Dict[str, Any] = {}
        self._current_model: Optional[str] = None
    
    @property
    def device(self) -> str:
        return self._device
    
    @property
    def dtype(self) -> torch.dtype:
        return self._dtype
    
    def load_model(self, model_type: ModelType) -> None:
        """
        加载模型到设备
        
        Args:
            model_type: 模型类型
        """
        if model_type.value in self._models:
            self._current_model = model_type.value
            return
        
        from src.hy3dshape import Hunyuan3DDiTFlowMatchingPipeline
        
        model_path = self._get_model_path(model_type)
        
        # 根据模型类型选择 subfolder
        subfolder = self._get_subfolder(model_type)
        
        # 根据模型类型选择是否使用 safetensors
        # Hunyuan3D-2.1 使用 .ckpt 格式，Hunyuan3D-2mv 使用 .safetensors 格式
        use_safetensors = self._get_use_safetensors(model_type)
        
        pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            model_path,
            device=self._device,
            dtype=self._dtype,
            subfolder=subfolder,
            use_safetensors=use_safetensors,
            variant='fp16'
        )
        
        self._models[model_type.value] = pipeline
        self._current_model = model_type.value
    
    def unload_model(self, model_type: ModelType) -> None:
        """
        从设备卸载模型
        
        Args:
            model_type: 模型类型
        """
        if model_type.value in self._models:
            del self._models[model_type.value]
            
            if self._current_model == model_type.value:
                self._current_model = None
            
            # 清理显存
            if self._device == "cuda":
                torch.cuda.empty_cache()
            elif self._device == "mps":
                torch.mps.empty_cache()
    
    def get_model(self, model_type: Optional[ModelType] = None) -> Any:
        """
        获取模型实例
        
        Args:
            model_type: 模型类型，None 时返回当前模型
            
        Returns:
            模型实例
            
        Raises:
            RuntimeError: 模型未加载
        """
        key = model_type.value if model_type else self._current_model
        if key is None or key not in self._models:
            raise RuntimeError(f"Model {key} not loaded")
        return self._models[key]
    
    def _get_model_path(self, model_type: ModelType) -> str:
        """获取模型路径"""
        paths = {
            ModelType.HUNYUAN3D_2_1: os.path.join(self.weights_dir, "Hunyuan3D-2.1"),
            ModelType.HUNYUAN3D_2MV: os.path.join(self.weights_dir, "Hunyuan3D-2mv"),
        }
        return paths[model_type]
    
    def _get_subfolder(self, model_type: ModelType) -> str:
        """获取模型子目录"""
        subfolders = {
            ModelType.HUNYUAN3D_2_1: "hunyuan3d-dit-v2-1",
            ModelType.HUNYUAN3D_2MV: "hunyuan3d-dit-v2-mv",
        }
        return subfolders[model_type]
    
    def _get_use_safetensors(self, model_type: ModelType) -> bool:
        """
        获取是否使用 safetensors 格式
        
        Hunyuan3D-2.1 使用 .ckpt 格式
        Hunyuan3D-2mv 使用 .safetensors 格式
        """
        use_safetensors_map = {
            ModelType.HUNYUAN3D_2_1: False,  # 使用 .ckpt
            ModelType.HUNYUAN3D_2MV: True,   # 使用 .safetensors
        }
        return use_safetensors_map[model_type]
    
    @property
    def loaded_models(self) -> List[str]:
        """获取已加载的模型列表"""
        return list(self._models.keys())
    
    @property
    def current_model(self) -> Optional[str]:
        """获取当前模型"""
        return self._current_model
    
    def get_gpu_memory_info(self) -> Dict[str, float]:
        """
        获取 GPU 显存信息
        
        Returns:
            包含 used 和 total 的字典（单位 GB）
        """
        if self._device == "cuda" and torch.cuda.is_available():
            return {
                "used": torch.cuda.memory_allocated() / 1024**3,
                "total": torch.cuda.get_device_properties(0).total_memory / 1024**3
            }
        elif self._device == "mps":
            # MPS 没有直接的显存查询 API
            return {"used": 0, "total": 0}
        return {"used": 0, "total": 0}
