// types/apiKeys.ts

/**
 * API 供应商枚举（与后端保持一致）
 */
export const ApiProvider = {
  OPENAI: "openai",
  SILICONFLOW: "siliconflow", 
  BCE_QIANFAN: "bce-qianfan",
  NVIDIA_NIM: "nvidia-nim",
  OLLAMA: "ollama"
} as const;

export type ApiProvider = typeof ApiProvider[keyof typeof ApiProvider];

/**
 * 供应商选项接口（用于下拉选择器）
 */
export interface ProviderOption {
  value: string;
  label: string;
}

/**
 * API Key 实体接口（与后端响应一致）
 */
export interface ApiKey {
  id: string;
  name: string;
  provider: ApiProvider;
  base_url: string;
  key_preview: string;
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
}

/**
 * 创建 API Key 请求接口（前端表单数据）
 */
export interface CreateApiKeyRequest {
  name: string;
  provider: ApiProvider;
  api_key: string;  // 明文密钥，将在前端加密
  base_url: string;
}

/**
 * 创建 API Key 响应接口
 */
export interface CreateApiKeyResponse {
  id: string;
  name: string;
  provider: ApiProvider;
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
  provider?: ApiProvider;
  base_url?: string;
  status?: 'active' | 'inactive';
}

/**
 * 获取供应商列表响应接口
 */
export interface GetProvidersResponse {
  providers: string[];
}

/**
 * 测试 API Key 响应接口
 */
export interface TestApiKeyResponse {
  success: boolean;
  message: string;
  response_time_ms: number | null;
  tested_at: string | null;
  status_code?: number;
}

/**
 * 分页列表响应接口
 */
export interface ApiKeyListResponse {
  items: ApiKey[];
  total: number;
  page: number;
  size: number;
  pages: number;
}