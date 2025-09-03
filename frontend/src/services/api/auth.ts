// 认证相关API - 使用主API客户端
import { apiClient } from './index';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  email: string;
  full_name: string | null;
}

export interface User {
  email: string;
  full_name: string | null;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}

export const authService = {
  // 登录 - 一次性获取所有需要的用户信息
  login: (credentials: LoginRequest) => 
    apiClient.post<LoginResponse>('/auth/login', credentials),

  // 注册
  register: (userData: RegisterRequest) => 
    apiClient.post<User>('/auth/register', userData),

  // 测试认证（可选，用于开发调试）
  testAuth: () => 
    apiClient.post('/auth/test-auth'),

  // 注意：不再需要getCurrentUser接口，登录时已获取所有必要信息
  // 如果将来需要更新用户信息，可以添加updateProfile等接口
};

export { authService as authApi };
export default authService;
