# -*- coding: utf-8 -*-
"""
响应模型定义
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateResponse(BaseModel):
    """生成响应"""
    task_id: str
    status: TaskStatus
    message: str


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: TaskStatus
    progress: Optional[float] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class TaskResultResponse(BaseModel):
    """任务结果响应"""
    task_id: str
    mesh_base64: str
    format: str
    processing_time: float
    config: Dict[str, Any]


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    is_ready: bool
    loaded_models: List[str]
    gpu_memory_used_gb: float
    gpu_memory_total_gb: float


class ModelInfo(BaseModel):
    """模型信息"""
    model_id: str
    name: str
    is_loaded: bool
    description: str


class ModelsResponse(BaseModel):
    """模型列表响应"""
    models: List[ModelInfo]


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    code: str
