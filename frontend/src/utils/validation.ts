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
  uri?: string;
  database_name?: string;
  token?: string;
}

export function validateMilvusConnectionForm(data: {
  name: string;
  description: string;
  uri: string;
  database_name: string;
  token: string;
}): MilvusConnectionValidationErrors {
  const errors: MilvusConnectionValidationErrors = {};

  // 验证名称
  if (!data.name.trim()) {
    errors.name = '请输入连接名称';
  } else if (!isValidLength(data.name, 1, 255)) {
    errors.name = '连接名称长度必须在1-255个字符之间';
  }

  // 验证 URI（完整的连接地址，可包含端口）
  if (!data.uri.trim()) {
    errors.uri = '请输入连接 URI';
  } else if (!isValidLength(data.uri, 1, 500)) {
    errors.uri = 'URI 长度必须在1-500个字符之间';
  } else {
    const trimmedUri = data.uri.trim();
    
    // 必须包含协议
    if (!trimmedUri.includes('://')) {
      errors.uri = 'URI 必须包含协议（如 http://localhost:19530 或 https://your-zilliz-cluster.vectordb.zillizcloud.com）';
    } else {
      try {
        const url = new URL(trimmedUri);
        if (!['http:', 'https:'].includes(url.protocol)) {
          errors.uri = '协议必须是 http 或 https';
        }
      } catch {
        errors.uri = '无效的 URI 格式，请输入完整的 URI（如 http://localhost:19530 或 https://your-cluster.vectordb.zillizcloud.com）';
      }
    }
  }

  // 验证数据库名称（必填）
  if (!data.database_name.trim()) {
    errors.database_name = '请输入数据库名称';
  } else if (!isValidLength(data.database_name, 1, 255)) {
    errors.database_name = '数据库名称长度必须在1-255个字符之间';
  }

  // 验证 token（必填）
  if (!data.token.trim()) {
    errors.token = '请输入认证 Token';
  } else if (!isValidLength(data.token, 1, 500)) {
    errors.token = 'Token 长度必须在1-500个字符之间';
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
    uri: string;
    database_name: string;
    token: string;
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

    case 'uri':
      if (!value || !value.toString().trim()) {
        return '请输入连接 URI';
      } else if (!isValidLength(value.toString(), 1, 500)) {
        return 'URI 长度必须在1-500个字符之间';
      } else {
        const trimmedUri = value.toString().trim();
        
        // 必须包含协议
        if (!trimmedUri.includes('://')) {
          return 'URI 必须包含协议（如 http://localhost:19530 或 https://your-zilliz-cluster.vectordb.zillizcloud.com）';
        } else {
          try {
            const url = new URL(trimmedUri);
            if (!['http:', 'https:'].includes(url.protocol)) {
              return '协议必须是 http 或 https';
            }
          } catch {
            return '无效的 URI 格式，请输入完整的 URI（如 http://localhost:19530 或 https://your-cluster.vectordb.zillizcloud.com）';
          }
        }
      }
      break;

    case 'database_name':
      if (!value || !value.toString().trim()) {
        return '请输入数据库名称';
      } else if (!isValidLength(value.toString(), 1, 255)) {
        return '数据库名称长度必须在1-255个字符之间';
      }
      break;

    case 'token':
      if (!value || !value.toString().trim()) {
        return '请输入认证 Token';
      } else if (!isValidLength(value.toString(), 1, 500)) {
        return 'Token 长度必须在1-500个字符之间';
      }
      break;

    default:
      return undefined;
  }

  return undefined;
}
