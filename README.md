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
│   │   ├── api/           # HTTP 接口层
│   │   │   └── v1/        # API 版本控制
│   │   │       ├── router.py          # 主路由聚合器
│   │   │       └── endpoints/         # 具体端点实现
│   │   │           ├── auth/          # 认证相关端点
│   │   │           │   ├── router.py  # ✅ 只处理：参数提取、依赖注入、HTTP状态码
│   │   │           │   └── dependencies.py # 认证依赖
│   │   │           ├── keys/          # API Key 管理端点
│   │   │           │   └── router.py  # ✅ 不包含：业务逻辑、外部API调用
│   │   │           └── embeddings/    # 嵌入向量端点
│   │   │               └── router.py  # ✅ 职责：RESTful 协议适配
│   │   ├── core/          # 核心配置
│   │   │   ├── config.py  # 项目配置
│   │   │   ├── crypto.py  # 加密系统 (RSA + AES)
│   │   │   ├── db.py      # 数据库连接
│   │   │   └── security.py # 认证安全
│   │   ├── crud/          # 数据访问层
│   │   │   ├── api_key.py # ✅ 处理：纯数据库操作、查询优化
│   │   │   ├── user.py    # ✅ 处理：数据权限过滤
│   │   │   └── base.py    # ✅ 职责：CRUD 基础操作
│   │   ├── llm_clients/   # 外部服务适配层
│   │   │   ├── base.py    # ✅ 职责：统一的外部服务接口
│   │   │   ├── factory.py # ✅ 处理：客户端创建、提供商适配
│   │   │   ├── openai_client.py  # ✅ 处理：协议转换、连接管理
│   │   │   └── ollama_client.py  # Ollama 客户端适配
│   │   ├── models/        # SQLAlchemy 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py    # 基础模型类
│   │   │   ├── user.py    # 用户模型
│   │   │   ├── api_key.py # API Key 模型
│   │   │   ├── connection.py      # Milvus 连接模型
│   │   │   └── upload_history.py  # 文件上传历史
│   │   ├── schemas/       # Pydantic 数据验证
│   │   │   ├── api_key.py # API Key 验证模式
│   │   │   ├── crypto.py  # 加密相关模式
│   │   │   └── user.py    # 用户验证模式
│   │   └── services/      # 业务逻辑层
│   │       ├── api_key_service.py  # ✅ 处理：API Key 管理业务流程
│   │       ├── embedding_service.py # ✅ 处理：向量化业务逻辑
│   │       └── milvus_service.py   # ✅ 职责：复杂业务规则、工作流协调
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
- **项目架构**：完整的分层架构设计（API + Service + CRUD + Client）
- **用户认证系统**：完整的登录注册、JWT 认证、权限管理
- **API Key 管理**：加密存储、多提供商支持、验证测试
- **嵌入服务架构**：统一的向量化接口、LLM 客户端工厂模式
- **安全系统**：RSA + AES 双重加密、密钥管理
- **前端组件库**：shadcn/ui + TailwindCSS v4 集成
- **数据库模型**：User、ApiKey 等核心模型完善

### 🚧 开发中
- **嵌入向量 API**：文本向量化接口实现
- **文件上传功能**：支持多种格式的数据上传
- **Milvus 集成**：向量数据库连接和操作

### 📋 待实现
- **Schema 管理器**：Milvus Collection 模板管理
- **数据导入流水线**：上传 → 向量化 → 加载的完整工作流
- **任务中心仪表盘**：后台任务状态监控和管理
- **检索与评估中心**：向量检索效果测试和评估
- **后台任务队列**：Celery + Redis 异步任务处理

### 🏗️ 架构优势
- **Linus 式设计**：简洁数据结构、消除特殊情况、实用主义导向
- **清晰分层**：API 层只处理 HTTP，Service 层处理业务逻辑，CRUD 层处理数据
- **统一错误处理**：避免重复代码，提供一致的用户体验
- **扩展性强**：新增 LLM 提供商只需实现客户端接口

## 🎯 分层架构最佳实践

### 📋 各层职责定义

#### **1. API 层 (`/api/v1/endpoints/`)**
```python
# ✅ 职责：HTTP 协议处理
@router.post("/{key_id}/test")
async def test_api_key(key_id: UUID, current_user: User, db: Session):
    result = api_key_service.validate_api_key(key_id, current_user.id, db)
    return format_response(result)

# ❌ 禁止：业务逻辑、外部 API 调用、复杂计算
```

#### **2. Service 层 (`/services/`)**
```python
# ✅ 职责：业务逻辑协调
def validate_api_key(self, key_id, user_id, db):
    api_key = self._get_validated_api_key(db, key_id, user_id)  # CRUD 调用
    client = self._get_llm_client(db, api_key)                 # Client 调用
    return client.validate_api_key()                           # 业务流程

# ❌ 禁止：HTTP 处理、直接 SQL 操作
```

#### **3. CRUD 层 (`/crud/`)**
```python
# ✅ 职责：数据库操作
def get(self, db: Session, id: UUID, user_id: UUID) -> Optional[ApiKey]:
    return db.query(ApiKey).filter(
        and_(ApiKey.id == id, ApiKey.user_id == user_id)
    ).first()

# ❌ 禁止：业务逻辑、外部服务调用
```

#### **4. Client 层 (`/llm_clients/`)**
```python
# ✅ 职责：外部服务适配
def validate_api_key(self) -> Tuple[bool, str]:
    client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    client.models.list()  # 统一的验证接口
    return True, "验证成功"

# ❌ 禁止：数据库操作、业务逻辑
```

### 🔄 数据流向图
```
HTTP Request → API 层 → Service 层 → CRUD 层 → Database
                ↓         ↓           ↓
           参数提取    业务逻辑    数据操作
                ↓         ↓           ↓  
           HTTP Response ← 结果处理 ← Client 层 ← External API
```