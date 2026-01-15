# -*- coding: utf-8 -*-
"""
推理流程编排器
"""

import time
import uuid
from typing import Union, Optional
from PIL import Image
from pathlib import Path

from .types import GenerationConfig, GenerationResult
from .model_manager import ModelManager


class PipelineOrchestrator:
    """推理流程编排器"""
    
    def __init__(
        self,
        model_manager: ModelManager,
        birefnet_path: str = "weights/BiRefNet"
    ):
        """
        初始化编排器
        
        Args:
            model_manager: 模型管理器
            birefnet_path: BiRefNet 模型路径
        """
        self.model_manager = model_manager
        self.birefnet_path = birefnet_path
        self._background_remover = None
        self._mesh_optimizer = None
        self._format_converter = None
    
    @property
    def background_remover(self):
        """延迟加载背景移除器"""
        if self._background_remover is None:
            from src.preprocessing import BiRefNetBackgroundRemover
            self._background_remover = BiRefNetBackgroundRemover(
                model_path=self.birefnet_path,
                device=self.model_manager.device
            )
        return self._background_remover
    
    @property
    def mesh_optimizer(self):
        """延迟加载 Mesh 优化器"""
        if self._mesh_optimizer is None:
            from src.postprocessing import MeshOptimizer
            self._mesh_optimizer = MeshOptimizer()
        return self._mesh_optimizer
    
    @property
    def format_converter(self):
        """延迟加载格式转换器"""
        if self._format_converter is None:
            from src.postprocessing import FormatConverter
            self._format_converter = FormatConverter()
        return self._format_converter
    
    def generate(
        self,
        image: Union[str, Path, Image.Image],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        执行完整的生成流程
        
        Args:
            image: 输入图像（路径或 PIL Image）
            config: 生成配置
            
        Returns:
            生成结果
        """
        config = config or GenerationConfig()
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 1. 加载图像
        if isinstance(image, (str, Path)):
            image = Image.open(image)
        
        # 2. 预处理（背景移除）
        if config.remove_background:
            preprocess_result = self.background_remover.process(image)
            image = preprocess_result["image"]
        
        # 3. 推理
        pipeline = self.model_manager.get_model()
        mesh = pipeline(
            image=image,
            num_inference_steps=config.num_inference_steps,
            guidance_scale=config.guidance_scale,
            octree_resolution=config.octree_resolution
        )
        
        # pipeline 返回列表，取第一个
        if isinstance(mesh, list):
            mesh = mesh[0]
        
        # 4. 后处理
        if config.optimize_mesh and mesh is not None:
            self.mesh_optimizer.max_faces = config.max_faces
            mesh = self.mesh_optimizer.process(mesh)
        
        processing_time = time.time() - start_time
        
        return GenerationResult(
            mesh=mesh,
            task_id=task_id,
            processing_time=processing_time,
            config=config
        )
    
    def unload_preprocessors(self):
        """卸载预处理器释放显存"""
        if self._background_remover is not None:
            self._background_remover.unload()
            self._background_remover = None
