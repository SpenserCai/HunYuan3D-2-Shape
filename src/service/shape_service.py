# -*- coding: utf-8 -*-
"""
Shape 生成服务 - 统一对外接口
"""

from typing import Union, Optional
from PIL import Image
from pathlib import Path

from .types import ModelType, GenerationConfig, GenerationResult, ServiceStatus
from .model_manager import ModelManager
from .pipeline_orchestrator import PipelineOrchestrator


class ShapeGenerationService:
    """Shape 生成服务 - 统一对外接口"""
    
    _instance: Optional['ShapeGenerationService'] = None
    
    def __init__(
        self,
        weights_dir: str = "weights",
        default_model: ModelType = ModelType.HUNYUAN3D_2_1,
        auto_load: bool = True,
        device: Optional[str] = None
    ):
        """
        初始化服务
        
        Args:
            weights_dir: 模型权重目录
            default_model: 默认模型类型
            auto_load: 是否自动加载默认模型
            device: 推理设备，None 时自动检测
        """
        self.model_manager = ModelManager(weights_dir, device=device)
        self.orchestrator = PipelineOrchestrator(
            self.model_manager,
            birefnet_path=f"{weights_dir}/BiRefNet"
        )
        
        if auto_load:
            self.model_manager.load_model(default_model)
    
    @classmethod
    def get_instance(
        cls,
        weights_dir: str = "weights",
        default_model: ModelType = ModelType.HUNYUAN3D_2_1,
        auto_load: bool = True,
        device: Optional[str] = None
    ) -> 'ShapeGenerationService':
        """
        获取单例实例
        
        Args:
            weights_dir: 模型权重目录
            default_model: 默认模型类型
            auto_load: 是否自动加载默认模型
            device: 推理设备
            
        Returns:
            服务实例
        """
        if cls._instance is None:
            cls._instance = cls(
                weights_dir=weights_dir,
                default_model=default_model,
                auto_load=auto_load,
                device=device
            )
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """重置单例实例"""
        cls._instance = None
    
    def generate(
        self,
        image: Union[str, Path, Image.Image],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        生成 3D 模型
        
        Args:
            image: 输入图像
            config: 生成配置
            
        Returns:
            生成结果
        """
        return self.orchestrator.generate(image, config)
    
    def load_model(self, model_type: ModelType) -> None:
        """
        加载指定模型
        
        Args:
            model_type: 模型类型
        """
        self.model_manager.load_model(model_type)
    
    def unload_model(self, model_type: ModelType) -> None:
        """
        卸载指定模型
        
        Args:
            model_type: 模型类型
        """
        self.model_manager.unload_model(model_type)
    
    def get_status(self) -> ServiceStatus:
        """
        获取服务状态
        
        Returns:
            服务状态
        """
        gpu_info = self.model_manager.get_gpu_memory_info()
        return ServiceStatus(
            is_ready=len(self.model_manager.loaded_models) > 0,
            loaded_models=self.model_manager.loaded_models,
            gpu_memory_used=gpu_info["used"],
            gpu_memory_total=gpu_info["total"]
        )
