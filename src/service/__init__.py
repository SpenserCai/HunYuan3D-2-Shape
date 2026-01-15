# -*- coding: utf-8 -*-
"""
服务层模块
提供统一的 Shape 生成服务接口
"""

from .shape_service import ShapeGenerationService
from .types import (
    ModelType,
    GenerationConfig,
    GenerationResult,
    ServiceStatus,
    InputMode,
    ViewType,
    MultiViewInput
)
from .model_manager import ModelManager
from .pipeline_orchestrator import PipelineOrchestrator

__all__ = [
    'ShapeGenerationService',
    'ModelType',
    'GenerationConfig',
    'GenerationResult',
    'ServiceStatus',
    'InputMode',
    'ViewType',
    'MultiViewInput',
    'ModelManager',
    'PipelineOrchestrator',
]
