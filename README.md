# VectorDB_Tools 项目文件夹结构

## 项目概述
这是一个围绕数据处理工作流的任务管理平台，从原始数据到 Milvus 可用数据的完整流水线。

## 实际项目结构

```
VectorDB_Tools/
├── LICENSE
├── README.md
├── backend/                # 后端服务 (FastAPI + SQLAlchemy)
│   ├── alembic/           # 数据库迁移文件
│   ├── alembic.ini        # Alembic 配置
│   ├── app/               # 核心应用代码
│   │   ├── api/           # API 路由层 (当前为空，待实现)
│   │   ├── core/          # 核心配置
│   │   │   ├── config.py  # 项目配置
│   │   │   └── db.py      # 数据库连接
│   │   ├── crud/          # 数据操作层 (当前为空)
│   │   ├── models/        # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── connection.py      # Milvus 连接模型
│   │   │   ├── upload_history.py  # 文件上传历史
│   │   │   └── user.py            # 用户模型
│   │   ├── schemas/       # Pydantic 数据验证 (当前为空)
│   │   └── services/      # 业务逻辑层
│   │       └── milvus_service.py  # Milvus 服务
│   ├── main.py            # FastAPI 应用入口
│   ├── pyproject.toml     # 项目依赖 (uv 管理)
│   ├── README.md          # 后端文档
│   ├── test/              # 测试代码
│   └── uv.lock            # 依赖锁定文件
└── frontend/              # 前端应用 (React + Vite)
    ├── components.json    # shadcn/ui 配置
    ├── eslint.config.js   # ESLint 配置
    ├── index.html         # HTML 入口
    ├── package.json       # 前端依赖 (pnpm 管理)
    ├── pnpm-lock.yaml     # 依赖锁定文件
    ├── public/            # 静态资源
    ├── README.md          # 前端文档
    ├── src/               # 源代码
    │   ├── api/           # API 调用封装
    │   │   └── connection.ts
    │   ├── App.css
    │   ├── App.tsx        # 根组件
    │   ├── assets/        # 静态资源
    │   ├── components/    # React 组件
    │   │   ├── common/    # 通用组件
    │   │   │   └── LanguageSwitcher.tsx
    │   │   ├── features/  # 功能组件
    │   │   │   ├── auth/          # 认证相关
    │   │   │   │   └── login-form.tsx
    │   │   │   ├── connection/    # 连接管理
    │   │   │   ├── dataUpload/    # 数据上传
    │   │   │   ├── profile/       # 用户配置
    │   │   │   └── vectorSearch/  # 向量搜索
    │   │   ├── layout/    # 布局组件
    │   │   │   ├── AppLayout.tsx
    │   │   │   └── AuthLayout.tsx
    │   │   └── ui/        # shadcn/ui 基础组件
    │   │       ├── button.tsx
    │   │       ├── card.tsx
    │   │       ├── input.tsx
    │   │       └── label.tsx
    │   ├── hooks/         # 自定义 Hooks
    │   ├── i18n.ts        # 国际化配置
    │   ├── index.css      # 全局样式
    │   ├── lib/           # 工具库
    │   │   ├── axios.ts   # HTTP 客户端
    │   │   └── utils.ts   # 工具函数
    │   ├── main.tsx       # React 入口
    │   ├── pages/         # 页面组件
    │   │   ├── auth/      # 认证页面
    │   │   ├── home/      # 首页
    │   │   └── NotFoundPage/  # 404页面
    │   ├── router/        # 路由配置
    │   ├── styles/        # 样式文件
    │   ├── types/         # TypeScript 类型定义
    │   ├── utils/         # 工具函数
    │   └── vite-env.d.ts  # Vite 类型声明
    ├── tsconfig.app.json  # TypeScript 应用配置
    ├── tsconfig.json      # TypeScript 主配置
    ├── tsconfig.node.json # TypeScript Node配置
    └── vite.config.ts     # Vite 构建配置
```

## 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **包管理**: uv (替代 pip/poetry)
- **数据库迁移**: Alembic
- **向量数据库**: Milvus

### 前端
- **框架**: React 19 + Vite
- **包管理**: pnpm
- **UI框架**: shadcn/ui + TailwindCSS v4
- **类型检查**: TypeScript
- **HTTP客户端**: Axios
- **国际化**: i18next

## 开发状态

### ✅ 已实现
- 基础项目结构搭建
- 用户认证界面
- Milvus 连接管理基础模型
- 前端组件库集成

### 🚧 开发中
- API 路由层实现
- 数据上传功能
- 向量搜索界面

### 📋 待实现
- Schema 管理器
- 数据导入流水线
- 任务中心仪表盘
- 检索与评估中心
- 后台任务队列 (Celery + Redis)