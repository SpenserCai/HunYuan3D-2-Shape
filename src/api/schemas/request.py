# -*- coding: utf-8 -*-
"""
请求模型定义
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum


class ModelTypeEnum(str, Enum):
    """模型类型枚举"""
    HUNYUAN3D_2_1 = "hunyuan3d-2.1"
    HUNYUAN3D_2MV = "hunyuan3d-2mv"


class InputModeEnum(str, Enum):
    """输入模式枚举"""
    SINGLE = "single"
    MULTI_VIEW = "multi_view"


class GenerateRequest(BaseModel):
    """单图生成请求"""
    image_base64: str = Field(..., description="Base64编码的图像")
    num_inference_steps: int = Field(50, ge=1, le=100, description="推理步数")
    guidance_scale: float = Field(5.0, ge=0, le=20, description="引导强度")
    octree_resolution: int = Field(384, ge=128, le=512, description="八叉树分辨率")
    remove_background: bool = Field(True, description="是否移除背景")
    optimize_mesh: bool = Field(True, description="是否优化Mesh")
    max_faces: int = Field(40000, ge=1000, le=200000, description="最大面数")
    output_format: str = Field("glb", description="输出格式")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "image_base64": "base64_encoded_image_data...",
                "num_inference_steps": 50,
                "guidance_scale": 5.0,
                "remove_background": True,
                "optimize_mesh": True,
                "max_faces": 40000,
                "output_format": "glb"
            }
        }
    }


class MultiViewGenerateRequest(BaseModel):
    """多视图生成请求"""
    views: Dict[str, str] = Field(
        ...,
        description="视图字典，key为视角名(front/left/back/right)，value为Base64编码的图像"
    )
    num_inference_steps: int = Field(50, ge=1, le=100, description="推理步数")
    guidance_scale: float = Field(5.0, ge=0, le=20, description="引导强度")
    octree_resolution: int = Field(384, ge=128, le=512, description="八叉树分辨率")
    remove_background: bool = Field(True, description="是否移除背景")
    optimize_mesh: bool = Field(True, description="是否优化Mesh")
    max_faces: int = Field(40000, ge=1000, le=200000, description="最大面数")
    output_format: str = Field("glb", description="输出格式")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "views": {
                    "front": "base64_front_image...",
                    "left": "base64_left_image...",
                    "back": "base64_back_image...",
                    "right": "base64_right_image..."
                },
                "num_inference_steps": 50,
                "guidance_scale": 5.0,
                "remove_background": True,
                "optimize_mesh": True,
                "max_faces": 40000,
                "output_format": "glb"
            }
        }
    }
