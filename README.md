# Milvus Tools 

backend/
├── alembic/             # Alembic 数据库迁移文件夹
│   └── versions/        # 自动生成的迁移脚本
├── app/                 # ✨ 核心：应用主代码目录
│   ├── api/             # API 层 (路由与端点)
│   │   └── endpoints/   # (示例) users.py, items.py
│   ├── core/            # 核心配置与服务
│   │   ├── config.py    # Pydantic 配置模块 (读取 .env)
│   │   └── db.py        # 数据库连接与会话管理
│   ├── crud/            # 数据操作层 (CRUD: Create, Read, Update, Delete)
│   ├── models/          # 数据库模型层 (SQLAlchemy Models)
│   │   ├── base.py      # DeclarativeBase 和 TimestampMixin
│   │   ├── user.py      # User 模型
│   │   └── __init__.py  # 模型“登记处”，供 Alembic 发现
│   └── schemas/         # 数据验证层 (Pydantic Schemas)
│       └── user.py      # User 的 Pydantic 模型
├── test/                # 测试代码目录
├── .env                 # 环境变量文件
├── .env.example         # 环境变量模板文件
├── alembic.ini          # Alembic 主配置文件
├── main.py              # FastAPI 应用入口文件
├── pyproject.toml       # 项目依赖与配置
└── README.md            # 后端专属的 README

frontend/
└── src/
    ├── api/               # (保留) 存放通用的 API 配置，如 Axios 实例
    ├── app/               # Redux Store 的配置
    ├── assets/            # (保留) 静态资源
    ├── components/        # (职责细分) 全局共享的 UI 组件
    │   ├── layout/        # 页面布局 (如 DashboardLayout, PageWrapper)
    │   └── ui/            # 基础 UI "积木" (Button, Input, Table, Spinner)
    ├── features/          # ✨ (核心新增) 按业务功能划分的模块
    │   ├── connection/    # 模块1: Milvus 连接管理
    │   │   ├── components/  # (ConnectionForm.tsx, ConnectionStatus.tsx)
    │   │   ├── index.tsx    # 连接页面的主组件
    │   │   └── connectionSlice.ts
    │   ├── dataUpload/    # 模块2: 数据上传与映射
    │   │   ├── components/  # (FileUpload.tsx, SchemaMapping.tsx, ProgressBar.tsx)
    │   │   ├── index.tsx    # 上传页面的主组件
    │   │   └── uploadSlice.ts
    │   └── vectorSearch/  # 模块3: 向量搜索测试
    │       ├── components/  # (SearchBar.tsx, SearchResults.tsx)
    │       ├── index.tsx    # 搜索页面的主组件
    │       └── searchSlice.ts
    ├── hooks/             # 全局共享的自定义 Hooks
    ├── lib/               # 第三方库的封装 (如 axios.ts)
    ├── pages/             # 页面组装层
    ├── router/            # 路由配置
    ├── styles/            # 全局样式
    ├── types/             # 全局 TypeScript 类型
    ├── utils/             # 全局工具函数
    └── ... (App.tsx, main.tsx)