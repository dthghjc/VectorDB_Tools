# 文件夹结构
backend/
├── alembic/              # Alembic 数据库迁移文件夹
├── app/                  # ✨ 核心：应用主代码目录
│   ├── api/              # API 层 (路由与端点)
│   │   └── endpoints/    # 按资源划分的路由文件 (e.g., connections.py, jobs.py)
│   ├── core/             # 核心配置与服务
│   │   ├── config.py     # Pydantic 配置模块 (读取 .env)
│   │   └── db.py         # 数据库连接与会话管理
│   ├── crud/             # 数据操作层 (仅包含纯粹的数据库 CRUD)
│   │   ├── crud_connection.py
│   │   └── crud_job.py
│   ├── models/           # 数据库模型层 (SQLAlchemy Models)
│   │   ├── base.py
│   │   ├── connection.py # Milvus 连接配置模型
│   │   └── job.py        # 后台任务状态模型
│   ├── schemas/          # 数据验证层 (Pydantic Schemas)
│   │   ├── connection.py
│   │   └── job.py
│   ├── services/         # ✨ 新增: 核心业务逻辑层
│   │   ├── embedding_service.py
│   │   └── milvus_service.py
│   └── tasks/            # ✨ 新增: Celery 后台任务定义
│       └── processing_tasks.py
├── test/                 # 测试代码目录
├── .env                  # 环境变量文件
├── .env.example          # 环境变量模板文件
├── alembic.ini           # Alembic 主配置文件
├── celery_worker.py      # ✨ 新增: Celery Worker 启动入口
├── main.py               # FastAPI 应用入口文件
├── pyproject.toml        # 项目依赖与配置 (Poetry)
└── README.md             # 后端专属 README

frontend/
└── src/
    ├── api/              # ✨ 职责明确: API 请求函数封装 (e.g., jobs.ts, search.ts)
    ├── app/              # Redux Store 的配置 (store.ts, rootReducer.ts)
    ├── assets/           # 静态资源 (images, fonts)
    ├── components/       # 全局共享的 UI 组件
    │   ├── layout/       # 页面布局 (e.g., DashboardLayout.tsx)
    │   └── ui/           # 基础 UI "积木", 由 shadcn/ui 生成 (e.g., Button.tsx, Table.tsx)
    ├── features/         # ✨ 核心: 按最终确定的五大模块划分
    │   ├── configuration/      # 模块1: 连接与密钥配置
    │   ├── schemaManager/      # 模块2: Schema 管理器
    │   ├── ingestionPipeline/  # 模块3: 数据导入流水线
    │   ├── taskDashboard/      # 模块4: 任务中心
    │   └── searchAndEval/      # 模块5: 检索与评估中心
    ├── hooks/            # 全局共享的自定义 Hooks (e.g., usePolling.ts)
    ├── lib/              # 第三方库的封装与配置 (e.g., axios.ts for axios instance)
    ├── router/           # 路由配置 (index.tsx)
    ├── styles/           # 全局样式 (globals.css)
    ├── types/            # 全局共享的 TypeScript 类型
    └── utils/            # 全局工具函数