# -*- coding: utf-8 -*-
"""
推理流程编排器
支持单图和多视图生成
"""

import time
import uuid
from typing import Union, Optional, Dict
from PIL import Image
from pathlib import Path

from .types import GenerationConfig, GenerationResult, InputMode, ModelType
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
        self._multi_view_processor = None
        self._mesh_optimizer = None
        self._format_converter = None
        self._lighting_normalizer = None
        self._advanced_mesh_optimizer = None
    
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
    def multi_view_processor(self):
        """延迟加载多视图处理器"""
        if self._multi_view_processor is None:
            from src.preprocessing import MultiViewProcessor
            self._multi_view_processor = MultiViewProcessor(
                background_remover=self.background_remover
            )
        return self._multi_view_processor
    
    @property
    def lighting_normalizer(self):
        """延迟加载光照校正器"""
        if self._lighting_normalizer is None:
            from src.preprocessing import LightingNormalizer
            self._lighting_normalizer = LightingNormalizer()
        return self._lighting_normalizer
    
    @property
    def mesh_optimizer(self):
        """延迟加载 Mesh 优化器"""
        if self._mesh_optimizer is None:
            from src.postprocessing import MeshOptimizer
            self._mesh_optimizer = MeshOptimizer()
        return self._mesh_optimizer
    
    @property
    def advanced_mesh_optimizer(self):
        """延迟加载高级 Mesh 优化器"""
        if self._advanced_mesh_optimizer is None:
            from src.postprocessing import AdvancedMeshOptimizer
            self._advanced_mesh_optimizer = AdvancedMeshOptimizer()
        return self._advanced_mesh_optimizer
    
    @property
    def format_converter(self):
        """延迟加载格式转换器"""
        if self._format_converter is None:
            from src.postprocessing import FormatConverter
            self._format_converter = FormatConverter()
        return self._format_converter
    
    def _detect_input_mode(
        self,
        image: Union[str, Path, Image.Image, Dict]
    ) -> InputMode:
        """
        自动检测输入模式
        
        Args:
            image: 输入图像或视图字典
            
        Returns:
            输入模式
        """
        if isinstance(image, dict):
            return InputMode.MULTI_VIEW
        return InputMode.SINGLE_IMAGE
    
    def generate(
        self,
        image: Union[str, Path, Image.Image, Dict[str, Union[str, Path, Image.Image]]],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        执行生成流程（支持单图和多视图）
        
        Args:
            image: 输入图像或多视图字典
                   单图模式: str/Path/PIL.Image
                   多视图模式: Dict[view_name, image]
            config: 生成配置
            
        Returns:
            生成结果
        """
        config = config or GenerationConfig()
        
        # 自动检测输入模式
        if config.auto_detect_mode:
            config.input_mode = self._detect_input_mode(image)
        
        # 根据模式选择生成方法
        if config.input_mode == InputMode.MULTI_VIEW:
            return self._generate_multi_view(image, config)
        else:
            return self._generate_single(image, config)
    
    def _generate_single(
        self,
        image: Union[str, Path, Image.Image],
        config: GenerationConfig
    ) -> GenerationResult:
        """
        单图生成流程
        
        Args:
            image: 输入图像
            config: 生成配置
            
        Returns:
            生成结果
        """
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 1. 加载图像
        if isinstance(image, (str, Path)):
            image = Image.open(image)
        
        # 2. 预处理（背景移除）
        if config.remove_background:
            preprocess_result = self.background_remover.process(image)
            image = preprocess_result["image"]
        
        # 3. 推理（使用 2.1 模型）
        pipeline = self.model_manager.get_model(ModelType.HUNYUAN3D_2_1)
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
        if mesh is not None:
            # 4.1 基础优化
            if config.optimize_mesh:
                self.mesh_optimizer.max_faces = config.max_faces
                mesh = self.mesh_optimizer.process(mesh)
            
            # 4.2 高级优化（如果启用）
            if any([config.fill_holes, config.make_watertight, 
                    config.smooth_surface, config.recalculate_normals]):
                mesh = self.advanced_mesh_optimizer.process(
                    mesh,
                    fill_holes=config.fill_holes,
                    max_hole_size=config.max_hole_size,
                    make_watertight=config.make_watertight,
                    smooth_surface=config.smooth_surface,
                    smooth_iterations=config.smooth_iterations,
                    recalculate_normals=config.recalculate_normals
                )
        
        processing_time = time.time() - start_time
        
        return GenerationResult(
            mesh=mesh,
            task_id=task_id,
            processing_time=processing_time,
            config=config,
            input_mode=InputMode.SINGLE_IMAGE,
            view_count=1
        )
    
    def _generate_multi_view(
        self,
        images: Dict[str, Union[str, Path, Image.Image]],
        config: GenerationConfig
    ) -> GenerationResult:
        """
        多视图生成流程
        
        Args:
            images: 视图字典 {view_name: image}
            config: 生成配置
            
        Returns:
            生成结果
        """
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 验证输入
        if not self.multi_view_processor.validate_views(images):
            raise ValueError("Multi-view input must contain at least 'front' view")
        
        view_count = len(images)
        
        # 1. 多视图预处理
        if config.remove_background:
            preprocess_result = self.multi_view_processor.process(
                images,
                remove_background=True
            )
            processed_views = preprocess_result["views"]
        else:
            # 加载图像但不移除背景
            processed_views = {}
            for view_name, img in images.items():
                if isinstance(img, (str, Path)):
                    img = Image.open(img)
                processed_views[view_name] = img
        
        # 1.5 光照一致性校正（如果启用）
        if config.normalize_lighting and len(processed_views) > 1:
            self.lighting_normalizer.method = config.lighting_method
            self.lighting_normalizer.strength = config.lighting_strength
            lighting_result = self.lighting_normalizer.process(processed_views)
            processed_views = lighting_result["views"]
        
        # 2. 确保多视图模型已加载
        if ModelType.HUNYUAN3D_2MV.value not in self.model_manager.loaded_models:
            self.model_manager.load_model(ModelType.HUNYUAN3D_2MV)
        
        # 3. 推理（使用 2mv 模型，传入字典格式）
        pipeline = self.model_manager.get_model(ModelType.HUNYUAN3D_2MV)
        mesh = pipeline(
            image=processed_views,  # 直接传入视图字典
            num_inference_steps=config.num_inference_steps,
            guidance_scale=config.guidance_scale,
            octree_resolution=config.octree_resolution
        )
        
        # pipeline 返回列表，取第一个
        if isinstance(mesh, list):
            mesh = mesh[0]
        
        # 4. 后处理
        if mesh is not None:
            # 4.1 基础优化
            if config.optimize_mesh:
                self.mesh_optimizer.max_faces = config.max_faces
                mesh = self.mesh_optimizer.process(mesh)
            
            # 4.2 高级优化（如果启用）
            if any([config.fill_holes, config.make_watertight, 
                    config.smooth_surface, config.recalculate_normals]):
                mesh = self.advanced_mesh_optimizer.process(
                    mesh,
                    fill_holes=config.fill_holes,
                    max_hole_size=config.max_hole_size,
                    make_watertight=config.make_watertight,
                    smooth_surface=config.smooth_surface,
                    smooth_iterations=config.smooth_iterations,
                    recalculate_normals=config.recalculate_normals
                )
        
        processing_time = time.time() - start_time
        
        return GenerationResult(
            mesh=mesh,
            task_id=task_id,
            processing_time=processing_time,
            config=config,
            input_mode=InputMode.MULTI_VIEW,
            view_count=view_count
        )
    
    def unload_preprocessors(self):
        """卸载预处理器释放显存"""
        if self._background_remover is not None:
            self._background_remover.unload()
            self._background_remover = None
        self._multi_view_processor = None
        self._lighting_normalizer = None
        self._advanced_mesh_optimizer = None
