# 认证系统设置指南

## 概述

已为 VectorDB Tools 项目实现了完整的 JWT 认证系统，包括用户注册、登录和认证保护的端点。

## 环境变量配置

在项目根目录创建 `.env` 文件，包含以下配置：

```env
# 数据库配置
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vectordb_tools

# JWT 配置
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API 端点

### 1. 用户注册
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password",
  "full_name": "User Name"
}
```

### 2. 用户登录
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

响应：
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

### 3. 获取当前用户信息
```
GET /api/v1/auth/me
Authorization: Bearer jwt_token_here
```

### 4. 测试认证
```
POST /api/v1/auth/test-auth
Authorization: Bearer jwt_token_here
```

## 启动应用

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

## 前端集成

前端可以通过以下方式使用认证：

1. 登录时保存 access_token
2. 在后续请求的 Authorization 头中携带：`Bearer ${access_token}`
3. Token 过期时重新登录

## 安全特性

- 密码使用 bcrypt 哈希加密
- JWT Token 包含过期时间
- 邮箱验证（使用 email-validator 包）
- 防止重复注册同一邮箱
- 用户激活状态检查

## 数据库迁移

确保运行了用户表的迁移：

```bash
cd backend
alembic upgrade head
```
