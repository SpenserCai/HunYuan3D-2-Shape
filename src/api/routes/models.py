# -*- coding: utf-8 -*-
"""
模型管理路由
"""

from fastapi import APIRouter, HTTPException

from ..schemas.response import ModelsResponse, ModelInfo
from src.service import ModelType

router = APIRouter(prefix="/api/v1", tags=["models"])

MODEL_DESCRIPTIONS = {
    "hunyuan3d-2.1": "Hunyuan3D 2.1 - 单图生成3D模型",
    "hunyuan3d-2mv": "Hunyuan3D 2MV - 多视图生成3D模型"
}


def get_service():
    """获取服务实例"""
    from src.service import ShapeGenerationService
    return ShapeGenerationService.get_instance(auto_load=False)


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """
    获取可用模型列表
    
    返回所有支持的模型及其加载状态
    """
    try:
        service = get_service()
        loaded = service.model_manager.loaded_models
    except Exception:
        loaded = []
    
    models = [
        ModelInfo(
            model_id=mt.value,
            name=mt.value,
            is_loaded=mt.value in loaded,
            description=MODEL_DESCRIPTIONS.get(mt.value, "")
        )
        for mt in ModelType
    ]
    
    return ModelsResponse(models=models)


@router.post("/models/{model_id}/load")
async def load_model(model_id: str):
    """
    加载模型
    
    Args:
        model_id: 模型 ID
    """
    try:
        model_type = ModelType(model_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    try:
        service = get_service()
        service.load_model(model_type)
        return {"message": f"Model {model_id} loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/unload")
async def unload_model(model_id: str):
    """
    卸载模型
    
    Args:
        model_id: 模型 ID
    """
    try:
        model_type = ModelType(model_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    try:
        service = get_service()
        service.unload_model(model_type)
        return {"message": f"Model {model_id} unloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
