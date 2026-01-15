# -*- coding: utf-8 -*-
"""
生成相关路由
"""

import base64
import io
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from PIL import Image

from ..schemas.request import GenerateRequest
from ..schemas.response import (
    GenerateResponse,
    TaskStatusResponse,
    TaskResultResponse,
    TaskStatus
)
from src.service import GenerationConfig

router = APIRouter(prefix="/api/v1", tags=["generate"])

# 简单的任务存储（生产环境应使用 Redis 等）
_tasks: Dict[str, Dict[str, Any]] = {}


def get_service():
    """获取服务实例"""
    from src.service import ShapeGenerationService
    return ShapeGenerationService.get_instance(auto_load=False)


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    提交 3D 生成任务
    
    接收 Base64 编码的图像，返回任务 ID
    """
    try:
        # 解码图像
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # 创建配置
        config = GenerationConfig(
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            octree_resolution=request.octree_resolution,
            remove_background=request.remove_background,
            optimize_mesh=request.optimize_mesh,
            max_faces=request.max_faces,
            output_format=request.output_format
        )
        
        # 获取服务实例
        service = get_service()
        
        # 同步执行（简化版，生产环境应使用异步任务队列）
        result = service.generate(image, config)
        
        # 存储结果
        _tasks[result.task_id] = {
            "status": TaskStatus.COMPLETED,
            "result": result,
            "created_at": datetime.now(),
            "completed_at": datetime.now()
        }
        
        return GenerateResponse(
            task_id=result.task_id,
            status=TaskStatus.COMPLETED,
            message="Generation completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    Args:
        task_id: 任务 ID
    """
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _tasks[task_id]
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        created_at=task.get("created_at"),
        completed_at=task.get("completed_at"),
        error=task.get("error")
    )


@router.get("/tasks/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: str):
    """
    获取任务结果
    
    Args:
        task_id: 任务 ID
        
    Returns:
        包含 Base64 编码 Mesh 的结果
    """
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _tasks[task_id]
    if task["status"] != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Task not completed")
    
    result = task["result"]
    
    # 导出 Mesh 为 Base64
    mesh_buffer = io.BytesIO()
    result.mesh.export(mesh_buffer, file_type=result.config.output_format)
    mesh_base64 = base64.b64encode(mesh_buffer.getvalue()).decode()
    
    return TaskResultResponse(
        task_id=task_id,
        mesh_base64=mesh_base64,
        format=result.config.output_format,
        processing_time=result.processing_time,
        config=result.config.to_dict()
    )
