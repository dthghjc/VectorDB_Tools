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

/**
 * 验证单个字段的 API Key 表单
 * @param field 要验证的字段名
 * @param value 字段值
 * @param formData 完整表单数据（用于关联验证）
 * @returns 该字段的错误信息，如果无错误则返回 undefined
 */
export function validateApiKeyField(
  field: keyof ApiKeyValidationErrors, 
  value: any, 
  _formData?: {
    name: string;
    provider: string;
    apiKey: string;
    baseUrl: string;
  }
): string | undefined {
  switch (field) {
    case 'name':
      if (!value || !value.toString().trim()) {
        return '请输入密钥名称';
      } else if (!isValidLength(value.toString(), 1, 255)) {
        return '名称长度必须在1-255个字符之间';
      }
      break;

    case 'provider':
      if (!value || !value.toString().trim()) {
        return '请选择服务提供商';
      } else if (!isValidProvider(value.toString())) {
        return '请选择有效的服务提供商';
      }
      break;

    case 'apiKey':
      if (!value || !value.toString().trim()) {
        return '请输入 API 密钥';
      }
      break;

    case 'baseUrl':
      if (!value || !value.toString().trim()) {
        return '请输入 API 基础 URL';
      } else if (!isValidUrl(value.toString())) {
        return '请输入有效的 URL 格式';
      } else if (!isValidLength(value.toString(), 1, 500)) {
        return 'URL 长度必须在1-500个字符之间';
      }
      break;

    default:
      return undefined;
  }

  return undefined;
}

/**
 * Milvus 连接创建表单验证
 */
export interface MilvusConnectionValidationErrors {
  name?: string;
  host?: string;
  port?: string;
  database_name?: string;
  username?: string;
  password?: string;
}

export function validateMilvusConnectionForm(data: {
  name: string;
  description: string;
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
}): MilvusConnectionValidationErrors {
  const errors: MilvusConnectionValidationErrors = {};

  // 验证名称
  if (!data.name.trim()) {
    errors.name = '请输入连接名称';
  } else if (!isValidLength(data.name, 1, 255)) {
    errors.name = '连接名称长度必须在1-255个字符之间';
  }

  // 验证主机地址（必须是完整 URL，包含协议）
  if (!data.host.trim()) {
    errors.host = '请输入主机地址';
  } else if (!isValidLength(data.host, 1, 500)) {
    errors.host = '主机地址长度必须在1-500个字符之间';
  } else {
    const trimmedHost = data.host.trim();
    
    // 必须包含协议
    if (!trimmedHost.includes('://')) {
      errors.host = '主机地址必须包含协议（如 http://localhost 或 https://example.com）';
    } else {
      try {
        const url = new URL(trimmedHost);
        if (!['http:', 'https:'].includes(url.protocol)) {
          errors.host = '协议必须是 http 或 https';
        }
        // 检查URL中是否包含端口，如果有则提示分别填写
        if (url.port) {
          errors.host = '请将端口在单独的端口字段中填写，主机地址中不要包含端口';
        }
      } catch {
        errors.host = '无效的 URL 格式，请输入完整的 URL（如 http://localhost 或 https://example.com）';
      }
    }
  }

  // 验证端口
  if (!data.port || data.port <= 0 || data.port > 65535) {
    errors.port = '端口必须在1-65535之间';
  }

  // 验证数据库名称（必填）
  if (!data.database_name.trim()) {
    errors.database_name = '请输入数据库名称';
  } else if (!isValidLength(data.database_name, 1, 255)) {
    errors.database_name = '数据库名称长度必须在1-255个字符之间';
  }

  // 验证用户名（必填）
  if (!data.username.trim()) {
    errors.username = '请输入用户名';
  } else if (!isValidLength(data.username, 1, 255)) {
    errors.username = '用户名长度必须在1-255个字符之间';
  }

  // 验证密码（必填）
  if (!data.password.trim()) {
    errors.password = '请输入密码';
  }

  return errors;
}

/**
 * 验证单个字段的 Milvus 连接表单
 * @param field 要验证的字段名
 * @param value 字段值
 * @param formData 完整表单数据（用于关联验证）
 * @returns 该字段的错误信息，如果无错误则返回 undefined
 */
export function validateMilvusConnectionField(
  field: keyof MilvusConnectionValidationErrors, 
  value: any, 
  _formData?: {
    name: string;
    description: string;
    host: string;
    port: number;
    database_name: string;
    username: string;
    password: string;
  }
): string | undefined {
  switch (field) {
    case 'name':
      if (!value || !value.toString().trim()) {
        return '请输入连接名称';
      } else if (!isValidLength(value.toString(), 1, 255)) {
        return '连接名称长度必须在1-255个字符之间';
      }
      break;

    case 'host':
      if (!value || !value.toString().trim()) {
        return '请输入主机地址';
      } else if (!isValidLength(value.toString(), 1, 500)) {
        return '主机地址长度必须在1-500个字符之间';
      } else {
        const trimmedHost = value.toString().trim();
        
        // 必须包含协议
        if (!trimmedHost.includes('://')) {
          return '主机地址必须包含协议（如 http://localhost 或 https://example.com）';
        } else {
          try {
            const url = new URL(trimmedHost);
            if (!['http:', 'https:'].includes(url.protocol)) {
              return '协议必须是 http 或 https';
            }
            // 检查URL中是否包含端口，如果有则提示分别填写
            if (url.port) {
              return '请将端口在单独的端口字段中填写，主机地址中不要包含端口';
            }
          } catch {
            return '无效的 URL 格式，请输入完整的 URL（如 http://localhost 或 https://example.com）';
          }
        }
      }
      break;

    case 'port':
      if (!value || value <= 0 || value > 65535) {
        return '端口必须在1-65535之间';
      }
      break;

    case 'database_name':
      if (!value || !value.toString().trim()) {
        return '请输入数据库名称';
      } else if (!isValidLength(value.toString(), 1, 255)) {
        return '数据库名称长度必须在1-255个字符之间';
      }
      break;

    case 'username':
      if (!value || !value.toString().trim()) {
        return '请输入用户名';
      } else if (!isValidLength(value.toString(), 1, 255)) {
        return '用户名长度必须在1-255个字符之间';
      }
      break;

    case 'password':
      if (!value || !value.toString().trim()) {
        return '请输入密码';
      }
      break;

    default:
      return undefined;
  }

  return undefined;
}
