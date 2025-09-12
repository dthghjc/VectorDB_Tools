// types/milvusConnections.ts

/**
 * Milvus 连接配置实体接口（与后端响应一致）
 */
export interface MilvusConnection {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  host: string;
  port: number;
  database_name: string;
  username: string;
  status: 'active' | 'inactive';
  last_used_at: string | null;
  usage_count: number;
  // 测试相关字段
  last_tested_at: string | null;
  test_status: 'success' | 'failed' | null;
  test_message: string | null;
  test_response_time: number | null;
  created_at: string;
  updated_at: string;
  connection_string: string;
}

/**
 * 创建 Milvus 连接请求接口（前端表单数据）
 */
export interface CreateMilvusConnectionRequest {
  name: string;
  description?: string;
  host: string;
  port: number;
  database_name: string;  // 必填
  username: string;      // 必填，明文用户名，将在前端加密
  password: string;      // 必填，明文密码，将在前端加密
}

/**
 * 创建 Milvus 连接响应接口
 */
export interface CreateMilvusConnectionResponse {
  id: string;
  name: string;
  description: string | null;
  host: string;
  port: number;
  database_name: string;
  username: string;
  status: 'active';
  usage_count: number;
  connection_string: string;
  created_at: string;
  updated_at: string;
  message: string;
}

/**
 * 更新 Milvus 连接请求接口
 */
export interface UpdateMilvusConnectionRequest {
  name?: string;
  description?: string;
  host?: string;
  port?: number;
  database_name?: string;
  status?: 'active' | 'inactive';
}

/**
 * 测试 Milvus 连接请求接口
 */
export interface TestMilvusConnectionRequest {
  timeout_seconds?: number;
}

/**
 * 测试 Milvus 连接响应接口
 */
export interface TestMilvusConnectionResponse {
  success: boolean;
  message: string;
  response_time_ms: number | null;
  tested_at: string | null;
  server_version?: string;
  collections_count?: number;
}

/**
 * 分页列表响应接口
 */
export interface MilvusConnectionListResponse {
  items: MilvusConnection[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Milvus 连接统计响应接口
 */
export interface MilvusConnectionStatsResponse {
  total: number;
  active: number;
  inactive: number;
  recently_used: number;
  by_status: Record<string, number>;
}

/**
 * 连接配置表单验证错误接口
 */
export interface MilvusConnectionValidationErrors {
  name?: string;
  host?: string;
  port?: string;
  database_name?: string;
  username?: string;
  password?: string;
}

/**
 * 连接配置表单数据接口
 */
export interface MilvusConnectionFormData {
  name: string;
  description: string;
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
}
