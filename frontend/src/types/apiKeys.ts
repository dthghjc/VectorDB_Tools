// types/apiKeys.ts

/**
 * API Key 实体接口（与后端响应一致）
 */
export interface ApiKey {
  id: string;
  name: string;
  provider: string;
  base_url: string;
  key_preview: string;
  status: 'active' | 'inactive';
  last_used_at: string | null;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * 创建 API Key 请求接口（前端表单数据）
 */
export interface CreateApiKeyRequest {
  name: string;
  provider: string;
  api_key: string;  // 明文密钥，将在前端加密
  base_url: string;
}

/**
 * 创建 API Key 响应接口
 */
export interface CreateApiKeyResponse {
  id: string;
  name: string;
  provider: string;
  base_url: string;
  key_preview: string;
  status: 'active';
  usage_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * 更新 API Key 请求接口
 */
export interface UpdateApiKeyRequest {
  name?: string;
  provider?: string;
  base_url?: string;
  status?: 'active' | 'inactive';
}