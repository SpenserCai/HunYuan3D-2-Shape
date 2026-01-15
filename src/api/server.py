# -*- coding: utf-8 -*-
"""
FastAPI 应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import generate, health, models
from .middleware import setup_error_handlers


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Hunyuan3D Shape Generation API",
        description="图像转3D模型生成服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 设置错误处理
    setup_error_handlers(app)
    
    # 注册路由
    app.include_router(generate.router)
    app.include_router(health.router)
    app.include_router(models.router)
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "name": "Hunyuan3D Shape Generation API",
            "version": "1.0.0",
            "docs": "/docs"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
