# Milvus Vector Tools

一个面向生产环境的 Milvus 向量数据库管理工具，基于 Python 构建，提供一个简洁的 Gradio 界面，支持自定义 schema、数据转换、API 向量生成与向量入库。

本工具**不负责查询和搜索**，仅专注于数据的预处理与存储，查询操作建议使用 Milvus 自带 Web UI。

---

## ✨ 功能特性

- 🔧 Schema 可视化定义（字段名 + 类型，支持多个向量字段）
- 📄 将 SVC 或 JSON 数据转为符合 schema 的 JSONL 格式
- 🧠 支持通过 OpenAI / BGE API 批量生成向量
- 📥 将带向量的数据写入对应 Milvus Collection
- 🔐 Gradio 登录保护，仅限授权用户访问
- 🐳 支持 Docker 部署，适配生产环境

---

## 🚀 快速开始

### 1. 安装依赖
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 `.env`
在项目根目录创建 `.env` 文件：
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=xxx
MYSQL_PASSWORD=xxx
MYSQL_DB=milvus_tool

OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1

BGE_API_KEY=xxx
BGE_BASE_URL=https://your-bge-endpoint/api

GRADIO_USERNAME=admin
GRADIO_PASSWORD=secure123
```

### 3. 启动服务
```bash
python app/main.py
```
访问地址将显示在终端输出，默认运行在本地。

---

## 🐳 Docker 部署

```bash
docker build -t milvus-vector-tools .
docker run --env-file .env -p 7860:7860 milvus-vector-tools
```

---

## 📂 项目结构
```
project-root/
├── app/                # 后端核心模块
├── ui/                 # Gradio 界面逻辑
├── schemas/            # 可选：schema 结构存档
├── data/               # 临时数据文件存储
├── config/             # 配置加载逻辑
├── logs/               # 日志输出目录
├── tests/              # 单元测试
├── .env                # 环境变量（未提交）
├── requirements.txt    # Python 依赖
├── Dockerfile          # 构建镜像
└── README.md           # 本文件
```

---

## 🧱 技术栈
- **后端**：Python 3.12 + SQLAlchemy + pymilvus
- **前端**：Gradio
- **数据库**：MySQL
- **向量模型**：OpenAI / BGE（通过 API）
- **部署**：Docker + Linux (Ubuntu 22.04)

---

## 📌 注意事项
- 请确保 Milvus 实例已启动并可连接（默认使用 pymilvus）
- 数据格式需完全符合 schema，否则写入将被拒绝
- 项目不包含搜索功能
- 所有敏感信息请勿提交至 Git（已在 .gitignore 中排除）

---

## 📄 License
MIT License

---

> 本项目持续开发中，欢迎提交 Issue 或 PR 🚀

