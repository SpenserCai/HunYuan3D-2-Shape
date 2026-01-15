# -*- coding: utf-8 -*-
"""
错误处理中间件
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback


def setup_error_handlers(app: FastAPI):
    """设置错误处理器"""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理"""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "code": "INTERNAL_ERROR"
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """值错误处理"""
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "detail": str(exc),
                "code": "VALIDATION_ERROR"
            }
        )
