#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端到端测试脚本
使用低参数进行快速测试
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, '.')

# 设置环境变量
os.environ['HY3DGEN_DEBUG'] = '0'


def test_birefnet_background_remover():
    """测试 BiRefNet 背景移除"""
    print("\n" + "=" * 50)
    print("Testing BiRefNet Background Remover...")
    print("=" * 50)
    
    from PIL import Image
    from src.preprocessing import BiRefNetBackgroundRemover
    
    # 创建测试图像
    test_image = Image.new('RGB', (256, 256), color='red')
    
    # 初始化背景移除器
    remover = BiRefNetBackgroundRemover(
        model_path="weights/BiRefNet",
        image_size=512  # 使用较小尺寸加速测试
    )
    
    print(f"Device: {remover.device}")
    
    # 处理图像
    result = remover.process(test_image)
    
    assert "image" in result
    assert "mask" in result
    assert result["image"].mode == "RGBA"
    
    print("✓ BiRefNet background remover test passed")
    
    # 卸载模型
    remover.unload()
    print("✓ Model unloaded")


def test_mesh_optimizer():
    """测试 Mesh 优化器"""
    print("\n" + "=" * 50)
    print("Testing Mesh Optimizer...")
    print("=" * 50)
    
    import trimesh
    import numpy as np
    from src.postprocessing import MeshOptimizer
    
    # 创建简单的测试 Mesh（立方体）
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
    ], dtype=np.float64)
    
    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # bottom
        [4, 6, 5], [4, 7, 6],  # top
        [0, 4, 5], [0, 5, 1],  # front
        [2, 6, 7], [2, 7, 3],  # back
        [0, 3, 7], [0, 7, 4],  # left
        [1, 5, 6], [1, 6, 2],  # right
    ])
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # 初始化优化器
    optimizer = MeshOptimizer(
        reduce_faces=True,
        max_faces=100,
        remove_floaters=True,
        remove_degenerate=True
    )
    
    # 处理 Mesh
    result = optimizer.process(mesh)
    
    assert isinstance(result, trimesh.Trimesh)
    assert len(result.vertices) > 0
    assert len(result.faces) > 0
    
    print(f"Original faces: {len(mesh.faces)}, Optimized faces: {len(result.faces)}")
    print("✓ Mesh optimizer test passed")


def test_format_converter():
    """测试格式转换器"""
    print("\n" + "=" * 50)
    print("Testing Format Converter...")
    print("=" * 50)
    
    import trimesh
    import numpy as np
    from src.postprocessing import FormatConverter
    
    # 创建简单的测试 Mesh
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [0.5, 1, 0]
    ], dtype=np.float64)
    faces = np.array([[0, 1, 2]])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    converter = FormatConverter()
    
    # 测试导出到临时文件
    with tempfile.NamedTemporaryFile(suffix='.glb', delete=False) as f:
        output_path = converter.export(mesh, f.name)
        assert os.path.exists(output_path)
        print(f"Exported to: {output_path}")
    
    # 测试转换为字节
    mesh_bytes = converter.to_bytes(mesh, format='glb')
    assert len(mesh_bytes) > 0
    print(f"Mesh bytes size: {len(mesh_bytes)}")
    
    print("✓ Format converter test passed")


def test_api_health():
    """测试 API 健康检查"""
    print("\n" + "=" * 50)
    print("Testing API Health Check...")
    print("=" * 50)
    
    from fastapi.testclient import TestClient
    from src.api import app
    
    client = TestClient(app)
    
    # 测试根路径
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    print(f"API Name: {data['name']}")
    
    # 测试健康检查
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    print(f"Health status: {data['status']}")
    print(f"Is ready: {data['is_ready']}")
    
    # 测试模型列表
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    print(f"Available models: {[m['model_id'] for m in data['models']]}")
    
    print("✓ API health check test passed")


def test_service_status():
    """测试服务状态"""
    print("\n" + "=" * 50)
    print("Testing Service Status...")
    print("=" * 50)
    
    from src.service import ShapeGenerationService, ModelType
    
    # 重置单例
    ShapeGenerationService.reset_instance()
    
    # 创建服务（不自动加载模型）
    service = ShapeGenerationService(
        weights_dir="weights",
        auto_load=False
    )
    
    status = service.get_status()
    print(f"Is ready: {status.is_ready}")
    print(f"Loaded models: {status.loaded_models}")
    print(f"GPU memory used: {status.gpu_memory_used:.2f} GB")
    print(f"GPU memory total: {status.gpu_memory_total:.2f} GB")
    
    print("✓ Service status test passed")


def main():
    print("=" * 60)
    print("Running End-to-End Tests (Low Parameters)")
    print("=" * 60)
    
    try:
        test_birefnet_background_remover()
        test_mesh_optimizer()
        test_format_converter()
        test_api_health()
        test_service_status()
        
        print("\n" + "=" * 60)
        print("All E2E tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
