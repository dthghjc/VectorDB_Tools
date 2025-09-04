// API Key 管理相关的 API 服务
import { apiClient } from './index';
import { rsaCrypto, encryptWithPublicKey } from '@/utils/crypto';
import type { 
  ApiKey, 
  CreateApiKeyRequest, 
  CreateApiKeyResponse 
} from '@/types/apiKeys';

/**
 * RSA 公钥响应接口
 */
interface RSAPublicKeyResponse {
  public_key: string;
}

/**
 * API Key 列表响应接口
 */
interface ApiKeyListResponse {
  items: ApiKey[];
  total: number;
  page: number;
  size: number;
}

/**
 * API Key 统计信息接口
 */
interface ApiKeyStats {
  total: number;
  active: number;
  inactive: number;
  by_provider: Record<string, number>;
}

/**
 * API Key 测试请求接口
 */
interface ApiKeyTestRequest {
  test_prompt: string;
}

/**
 * API Key 测试响应接口
 */
interface ApiKeyTestResponse {
  success: boolean;
  response_preview: string;
  error_message?: string;
}

/**
 * API Key 管理服务
 */
export const apiKeyService = {
  /**
   * 获取 RSA 公钥（用于前端加密）
   */
  getPublicKey: async (): Promise<string> => {
    const response = await apiClient.get<RSAPublicKeyResponse>('/keys/public-key');
    return response.data.public_key;
  },

  /**
   * 创建新的 API Key
   * 
   * 实现加密流程：
   * 1. 获取 RSA 公钥
   * 2. 使用公钥加密 API Key
   * 3. 发送加密后的数据到后端
   */
  create: async (data: CreateApiKeyRequest): Promise<CreateApiKeyResponse> => {
    // 第一步：获取公钥
    let publicKey: string;
    try {
      publicKey = await apiKeyService.getPublicKey();
    } catch (error) {
      throw new Error(`获取加密公钥失败: ${error}`);
    }

    // 第二步：加密 API Key
    let encryptedApiKey: string;
    try {
      encryptedApiKey = encryptWithPublicKey(data.api_key, publicKey);
    } catch (error) {
      throw new Error(`API Key 加密失败: ${error}`);
    }

    // 第三步：发送加密数据
    const encryptedRequest = {
      name: data.name,
      provider: data.provider,
      base_url: data.base_url,
      encrypted_api_key: encryptedApiKey  // 发送加密后的密钥
    };

    const response = await apiClient.post<CreateApiKeyResponse>('/keys/', encryptedRequest);
    return response.data;
  },

  /**
   * 获取 API Key 列表（分页）
   */
  getList: async (page: number = 1, size: number = 10): Promise<ApiKeyListResponse> => {
    const response = await apiClient.get<ApiKeyListResponse>('/keys/', {
      params: { page, size }
    });
    return response.data;
  },

  /**
   * 获取单个 API Key 详情
   */
  getById: async (id: string): Promise<ApiKey> => {
    const response = await apiClient.get<ApiKey>(`/keys/${id}`);
    return response.data;
  },

  /**
   * 更新 API Key
   */
  update: async (id: string, data: { name?: string; provider?: string; base_url?: string; status?: 'active' | 'inactive' }): Promise<ApiKey> => {
    const response = await apiClient.put<ApiKey>(`/keys/${id}`, data);
    return response.data;
  },

  /**
   * 删除 API Key
   */
  delete: async (id: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/keys/${id}`);
    return response.data;
  },

  /**
   * 测试 API Key 可用性
   */
  test: async (id: string, testRequest: ApiKeyTestRequest): Promise<ApiKeyTestResponse> => {
    const response = await apiClient.post<ApiKeyTestResponse>(`/keys/${id}/test`, testRequest);
    return response.data;
  },

  /**
   * 获取用户 API Key 统计信息
   */
  getStats: async (): Promise<ApiKeyStats> => {
    const response = await apiClient.get<ApiKeyStats>('/keys/stats/summary');
    return response.data;
  }
};

/**
 * 导出便捷的别名
 */
export { apiKeyService as apiKeyApi };
export default apiKeyService;
