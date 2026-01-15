#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多视图功能测试脚本
"""

import sys
sys.path.insert(0, '.')

from PIL import Image


def test_multi_view_processor():
    """测试多视图预处理器"""
    print("\n" + "=" * 50)
    print("Testing MultiViewProcessor...")
    print("=" * 50)
    
    from src.preprocessing import MultiViewProcessor
    
    # 创建测试图像
    test_images = {
        'front': Image.new('RGB', (256, 256), color='red'),
        'left': Image.new('RGB', (256, 256), color='green'),
        'back': Image.new('RGB', (256, 256), color='blue'),
        'right': Image.new('RGB', (256, 256), color='yellow')
    }
    
    # 初始化处理器（不使用背景移除）
    processor = MultiViewProcessor(background_remover=None)
    
    # 验证视图
    assert processor.validate_views(test_images), "Should validate with front view"
    assert processor.validate_views({'front': test_images['front']}), "Should validate with only front"
    assert not processor.validate_views({'left': test_images['left']}), "Should fail without front"
    
    # 处理图像
    result = processor.process(test_images, remove_background=False)
    
    assert result["view_count"] == 4
    assert set(result["available_views"]) == {'front', 'left', 'back', 'right'}
    assert all(v in result["views"] for v in ['front', 'left', 'back', 'right'])
    
    print(f"View count: {result['view_count']}")
    print(f"Available views: {result['available_views']}")
    print("✓ MultiViewProcessor test passed")


def test_multi_view_types():
    """测试多视图类型定义"""
    print("\n" + "=" * 50)
    print("Testing Multi-View Types...")
    print("=" * 50)
    
    from src.service import InputMode, ViewType, MultiViewInput, GenerationConfig
    
    # 测试 InputMode
    assert InputMode.SINGLE_IMAGE.value == "single"
    assert InputMode.MULTI_VIEW.value == "multi_view"
    print("✓ InputMode enum OK")
    
    # 测试 ViewType
    assert ViewType.FRONT.value == "front"
    assert ViewType.LEFT.value == "left"
    assert ViewType.BACK.value == "back"
    assert ViewType.RIGHT.value == "right"
    print("✓ ViewType enum OK")
    
    # 测试 MultiViewInput
    mv_input = MultiViewInput(views={
        'front': 'front.png',
        'left': 'left.png'
    })
    assert mv_input.view_count == 2
    assert mv_input.validate() == True
    assert 'front' in mv_input.available_views
    print(f"✓ MultiViewInput: {mv_input.view_count} views, valid={mv_input.validate()}")
    
    # 测试无 front 视图
    mv_input_invalid = MultiViewInput(views={'left': 'left.png'})
    assert mv_input_invalid.validate() == False
    print("✓ MultiViewInput validation (no front) OK")
    
    # 测试 GenerationConfig 多视图模式
    config = GenerationConfig(input_mode=InputMode.MULTI_VIEW)
    assert config.input_mode == InputMode.MULTI_VIEW
    config_dict = config.to_dict()
    assert config_dict['input_mode'] == 'multi_view'
    print("✓ GenerationConfig with multi-view mode OK")


def test_api_multi_view_endpoint():
    """测试多视图 API 端点"""
    print("\n" + "=" * 50)
    print("Testing Multi-View API Endpoint...")
    print("=" * 50)
    
    import base64
    import io
    from fastapi.testclient import TestClient
    from src.api import app
    
    client = TestClient(app)
    
    # 检查端点存在
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    assert '/api/v1/generate/multi-view' in routes
    print("✓ Multi-view endpoint registered")
    
    # 创建测试图像
    def image_to_base64(img):
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    test_images = {
        'front': image_to_base64(Image.new('RGB', (64, 64), color='red')),
        'left': image_to_base64(Image.new('RGB', (64, 64), color='green'))
    }
    
    # 测试缺少 front 视图的请求
    response = client.post('/api/v1/generate/multi-view', json={
        'views': {'left': test_images['left']},
        'num_inference_steps': 10
    })
    assert response.status_code == 400
    assert 'front' in response.json()['detail'].lower()
    print("✓ Validation: requires front view")
    
    # 测试无效视角名称
    response = client.post('/api/v1/generate/multi-view', json={
        'views': {
            'front': test_images['front'],
            'invalid_view': test_images['left']
        },
        'num_inference_steps': 10
    })
    assert response.status_code == 400
    assert 'invalid' in response.json()['detail'].lower()
    print("✓ Validation: rejects invalid view names")
    
    print("✓ Multi-view API endpoint tests passed")


def test_pipeline_orchestrator_mode_detection():
    """测试流程编排器的模式检测"""
    print("\n" + "=" * 50)
    print("Testing PipelineOrchestrator Mode Detection...")
    print("=" * 50)
    
    from src.service import PipelineOrchestrator, ModelManager, InputMode
    
    # 创建编排器（不加载模型）
    manager = ModelManager(weights_dir="weights")
    orchestrator = PipelineOrchestrator(manager)
    
    # 测试单图检测
    single_image = Image.new('RGB', (64, 64), color='red')
    mode = orchestrator._detect_input_mode(single_image)
    assert mode == InputMode.SINGLE_IMAGE
    print("✓ Single image detection OK")
    
    # 测试多视图检测
    multi_view = {'front': single_image, 'left': single_image}
    mode = orchestrator._detect_input_mode(multi_view)
    assert mode == InputMode.MULTI_VIEW
    print("✓ Multi-view detection OK")
    
    # 测试路径检测
    mode = orchestrator._detect_input_mode("path/to/image.png")
    assert mode == InputMode.SINGLE_IMAGE
    print("✓ Path input detection OK")


def main():
    print("=" * 60)
    print("Running Multi-View Feature Tests")
    print("=" * 60)
    
    try:
        test_multi_view_types()
        test_multi_view_processor()
        test_pipeline_orchestrator_mode_detection()
        test_api_multi_view_endpoint()
        
        print("\n" + "=" * 60)
        print("All multi-view tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
