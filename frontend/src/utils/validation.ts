/**
 * 表单验证工具函数
 */

import { ApiProvider } from '@/types/apiKeys';

/**
 * 验证 URL 格式
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}


/**
 * 验证字段长度
 */
export function isValidLength(value: string, min: number, max: number): boolean {
  const length = value.trim().length;
  return length >= min && length <= max;
}

/**
 * 验证API供应商是否有效
 */
export function isValidProvider(provider: string): boolean {
  return Object.values(ApiProvider).includes(provider as ApiProvider);
}

/**
 * API Key 创建表单验证
 */
export interface ApiKeyValidationErrors {
  name?: string;
  provider?: string;
  apiKey?: string;
  baseUrl?: string;
}

export function validateApiKeyForm(data: {
  name: string;
  provider: ApiProvider | string;
  apiKey: string;
  baseUrl: string;
}): ApiKeyValidationErrors {
  const errors: ApiKeyValidationErrors = {};

  // 验证名称
  if (!data.name.trim()) {
    errors.name = '请输入密钥名称';
  } else if (!isValidLength(data.name, 1, 255)) {
    errors.name = '名称长度必须在1-255个字符之间';
  }

  // 验证提供商
  if (!data.provider || !data.provider.toString().trim()) {
    errors.provider = '请选择服务提供商';
  } else if (!isValidProvider(data.provider.toString())) {
    errors.provider = '请选择有效的服务提供商';
  }

  // 验证 API Key（只检查非空）
  if (!data.apiKey.trim()) {
    errors.apiKey = '请输入 API 密钥';
  }

  // 验证 Base URL
  if (!data.baseUrl.trim()) {
    errors.baseUrl = '请输入 API 基础 URL';
  } else if (!isValidUrl(data.baseUrl)) {
    errors.baseUrl = '请输入有效的 URL 格式';
  } else if (!isValidLength(data.baseUrl, 1, 500)) {
    errors.baseUrl = 'URL 长度必须在1-500个字符之间';
  }

  return errors;
}
