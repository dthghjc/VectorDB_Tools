import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.crypto import initialize_crypto

# 启动前检查所有必要的加密密钥
try:
    settings.validate_crypto_keys()
    print("✅ 加密密钥配置检查通过")
except ValueError as e:
    print(str(e))
    sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化加密系统
    initialize_crypto()
    yield
    # 关闭时的清理（如果需要）

# 创建 FastAPI 应用实例
app = FastAPI(
    title="VectorDB Tools API",
    description="A comprehensive tool for managing vector databases and data processing workflows",
    version="1.0.0",
    lifespan=lifespan,
    # 禁用默认的 docs，我们将创建自定义的
    docs_url=None,
    redoc_url=None
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")



@app.get("/docs", response_class=HTMLResponse)
async def custom_swagger_ui_html():
    """自定义 Swagger UI，使用国内可访问的 CDN"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <title>VectorDB Tools API - Swagger UI</title>
    </head>
    <body>
        <div id="swagger-ui">
        </div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
        const ui = SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: "#swagger-ui",
            layout: "BaseLayout",
            deepLinking: true,
            showExtensions: true,
            showCommonExtensions: true,
            syntaxHighlight: {
                theme: "obsidian"
            },
            tryItOutEnabled: true,
        })
        </script>
    </body>
    </html>
    """, status_code=200)


@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "Welcome to VectorDB Tools API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
