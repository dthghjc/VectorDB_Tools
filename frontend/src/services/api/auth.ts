// 认证相关API - 使用主API客户端
import { apiClient } from './index';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export const authService = {
  // 登录
  login: (credentials: LoginRequest) => 
    apiClient.post<LoginResponse>('/auth/login', credentials),

  // 注册
  register: (userData: RegisterRequest) => 
    apiClient.post<User>('/auth/register', userData),

  // 获取当前用户信息
  getCurrentUser: () => 
    apiClient.get<User>('/auth/me'),

  // 测试认证（可选，用于开发调试）
  testAuth: () => 
    apiClient.post('/auth/test-auth'),
};

export { authService as authApi };
export default authService;
