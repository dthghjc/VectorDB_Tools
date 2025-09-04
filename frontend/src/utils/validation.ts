/**
 * 表单验证工具函数
 */

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
  provider: string;
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
  if (!data.provider.trim()) {
    errors.provider = '请输入服务提供商';
  } else if (!isValidLength(data.provider, 1, 100)) {
    errors.provider = '提供商名称长度必须在1-100个字符之间';
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
