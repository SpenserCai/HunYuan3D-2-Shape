# -*- coding: utf-8 -*-
"""
自研预处理模块
包含背景移除、图像预处理、多视图处理、光照校正等功能
"""

from .base import BasePreprocessor
from .background_remover import BiRefNetBackgroundRemover
from .image_processor import ImageEnhancer
from .pipeline import PreprocessingPipeline
from .multi_view_processor import MultiViewProcessor
from .lighting_normalizer import LightingNormalizer

__all__ = [
    'BasePreprocessor',
    'BiRefNetBackgroundRemover',
    'ImageEnhancer',
    'PreprocessingPipeline',
    'MultiViewProcessor',
    'LightingNormalizer',
]
