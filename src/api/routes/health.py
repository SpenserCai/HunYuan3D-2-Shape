# -*- coding: utf-8 -*-
"""
健康检查路由
"""

from fastapi import APIRouter

from ..schemas.response import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


def get_service():
    """获取服务实例（延迟导入避免循环依赖）"""
    from src.service import ShapeGenerationService
    return ShapeGenerationService.get_instance(auto_load=False)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查
    
    返回服务状态、已加载模型和 GPU 显存信息
    """
    try:
        service = get_service()
        status = service.get_status()
        
        return HealthResponse(
            status="healthy" if status.is_ready else "not_ready",
            is_ready=status.is_ready,
            loaded_models=status.loaded_models,
            gpu_memory_used_gb=status.gpu_memory_used,
            gpu_memory_total_gb=status.gpu_memory_total
        )
    except Exception:
        return HealthResponse(
            status="not_initialized",
            is_ready=False,
            loaded_models=[],
            gpu_memory_used_gb=0,
            gpu_memory_total_gb=0
        )
