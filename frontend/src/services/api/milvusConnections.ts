// Milvus 连接管理相关的 API 服务
import { apiClient } from './index';
import { encryptWithPublicKey } from '@/utils/crypto';
import type { 
  MilvusConnection, 
  CreateMilvusConnectionRequest, 
  CreateMilvusConnectionResponse,
  UpdateMilvusConnectionRequest,
  TestMilvusConnectionRequest,
  TestMilvusConnectionResponse,
  MilvusConnectionListResponse,
  MilvusConnectionStatsResponse
} from '@/types/milvusConnections';

/**
 * RSA 公钥响应接口
 */
interface RSAPublicKeyResponse {
  public_key: string;
}

/**
 * Milvus 连接管理服务
 */
export const milvusConnectionService = {
  /**
   * 获取 RSA 公钥（用于前端加密）
   */
  getPublicKey: async (): Promise<string> => {
    const response = await apiClient.get<RSAPublicKeyResponse>('/connections/public-key');
    return response.data.public_key;
  },

  /**
   * 创建新的 Milvus 连接配置
   * 
   * 实现加密流程：
   * 1. 获取 RSA 公钥
   * 2. 使用公钥加密认证信息（如果提供）
   * 3. 发送加密后的数据到后端
   */
  create: async (data: CreateMilvusConnectionRequest): Promise<CreateMilvusConnectionResponse> => {
    let encryptedUsername: string | undefined;
    let encryptedPassword: string | undefined;

    // 如果提供了认证信息，则进行加密
    if (data.username && data.password) {
      // 第一步：获取公钥
      let publicKey: string;
      try {
        publicKey = await milvusConnectionService.getPublicKey();
      } catch (error) {
        throw new Error(`获取加密公钥失败: ${error}`);
      }

      // 第二步：加密认证信息
      try {
        encryptedUsername = encryptWithPublicKey(data.username, publicKey);
        encryptedPassword = encryptWithPublicKey(data.password, publicKey);
      } catch (error) {
        throw new Error(`认证信息加密失败: ${error}`);
      }
    }

    // 第三步：发送加密数据
    const encryptedRequest = {
      name: data.name,
      description: data.description,
      host: data.host,
      port: data.port,
      database_name: data.database_name,
      encrypted_username: encryptedUsername,
      encrypted_password: encryptedPassword,
    };

    const response = await apiClient.post<CreateMilvusConnectionResponse>('/connections/', encryptedRequest);
    return response.data;
  },

  /**
   * 获取 Milvus 连接配置列表（分页）
   */
  getList: async (
    page: number = 1, 
    size: number = 10,
    status?: 'active' | 'inactive'
  ): Promise<MilvusConnectionListResponse> => {
    const params: Record<string, any> = { page, size };
    if (status) params.status = status;

    const response = await apiClient.get<MilvusConnectionListResponse>('/connections/', {
      params
    });
    return response.data;
  },

  /**
   * 获取单个 Milvus 连接配置详情
   */
  getById: async (id: string): Promise<MilvusConnection> => {
    const response = await apiClient.get<MilvusConnection>(`/connections/${id}`);
    return response.data;
  },

  /**
   * 更新 Milvus 连接配置
   */
  update: async (id: string, data: UpdateMilvusConnectionRequest): Promise<MilvusConnection> => {
    const response = await apiClient.put<MilvusConnection>(`/connections/${id}`, data);
    return response.data;
  },

  /**
   * 删除 Milvus 连接配置
   */
  delete: async (id: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/connections/${id}`);
    return response.data;
  },

  /**
   * 测试 Milvus 连接配置可用性
   */
  test: async (id: string, options?: TestMilvusConnectionRequest): Promise<TestMilvusConnectionResponse> => {
    const requestData = {
      timeout_seconds: options?.timeout_seconds || 10
    };
    const response = await apiClient.post<TestMilvusConnectionResponse>(`/connections/${id}/test`, requestData);
    return response.data;
  },

  /**
   * 获取用户 Milvus 连接配置统计信息
   */
  getStats: async (): Promise<MilvusConnectionStatsResponse> => {
    const response = await apiClient.get<MilvusConnectionStatsResponse>('/connections/stats/summary');
    return response.data;
  }
};

/**
 * 导出便捷的别名
 */
export { milvusConnectionService as milvusConnectionApi };
export default milvusConnectionService;
