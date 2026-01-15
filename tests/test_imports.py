#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模块导入测试
"""

import sys
sys.path.insert(0, '.')


def test_preprocessing_imports():
    """测试预处理模块导入"""
    from src.preprocessing import (
        BasePreprocessor,
        BiRefNetBackgroundRemover,
        ImageEnhancer,
        PreprocessingPipeline
    )
    print("✓ Preprocessing module imports OK")


def test_postprocessing_imports():
    """测试后处理模块导入"""
    from src.postprocessing import (
        BasePostprocessor,
        MeshOptimizer,
        FormatConverter,
        PostprocessingPipeline
    )
    print("✓ Postprocessing module imports OK")


def test_service_imports():
    """测试服务层模块导入"""
    from src.service import (
        ShapeGenerationService,
        ModelType,
        GenerationConfig,
        GenerationResult,
        ServiceStatus,
        ModelManager,
        PipelineOrchestrator
    )
    print("✓ Service module imports OK")


def test_api_imports():
    """测试 API 模块导入"""
    from src.api import create_app, app
    from src.api.schemas import (
        GenerateRequest,
        GenerateResponse,
        TaskStatus,
        HealthResponse,
        ModelsResponse
    )
    print("✓ API module imports OK")


def test_hy3dshape_imports():
    """测试 hy3dshape 核心模块导入"""
    from src.hy3dshape import (
        Hunyuan3DDiTPipeline,
        Hunyuan3DDiTFlowMatchingPipeline,
        FaceReducer,
        FloaterRemover,
        DegenerateFaceRemover,
        ImageProcessorV2
    )
    print("✓ hy3dshape module imports OK")


def main():
    print("=" * 50)
    print("Running import tests...")
    print("=" * 50)
    
    test_preprocessing_imports()
    test_postprocessing_imports()
    test_service_imports()
    test_api_imports()
    test_hy3dshape_imports()
    
    print("=" * 50)
    print("All import tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
