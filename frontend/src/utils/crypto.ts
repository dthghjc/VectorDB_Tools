import forge from 'node-forge';

/**
 * RSA 加密工具类
 * 
 * 实现前端 RSA 公钥加密，配合后端私钥解密
 * 这是双重加密架构的第一层：前端传输加密
 */
export class RSACrypto {
  private publicKey: forge.pki.rsa.PublicKey | null = null;

  /**
   * 从 PEM 格式的公钥字符串初始化
   */
  setPublicKeyFromPem(publicKeyPem: string): void {
    try {
      this.publicKey = forge.pki.publicKeyFromPem(publicKeyPem);
    } catch (error) {
      throw new Error(`无效的公钥格式: ${error}`);
    }
  }

  /**
   * 使用 RSA 公钥加密数据
   * 
   * @param data 要加密的明文数据
   * @returns Base64 编码的密文
   */
  encrypt(data: string): string {
    if (!this.publicKey) {
      throw new Error('未设置公钥，请先调用 setPublicKeyFromPem()');
    }

    try {
      // RSA 加密，使用 OAEP 填充，配置SHA256（与后端匹配）
      const encrypted = this.publicKey.encrypt(data, 'RSA-OAEP', {
        md: forge.md.sha256.create(),
        mgf1: {
          md: forge.md.sha256.create()
        }
      });
      // 转换为 Base64 便于传输
      return forge.util.encode64(encrypted);
    } catch (error) {
      throw new Error(`RSA 加密失败: ${error}`);
    }
  }

  /**
   * 检查是否已设置公钥
   */
  isReady(): boolean {
    return this.publicKey !== null;
  }
}

/**
 * 全局 RSA 加密实例
 */
export const rsaCrypto = new RSACrypto();

/**
 * 便捷的加密函数
 * 
 * @param data 要加密的数据
 * @param publicKeyPem PEM 格式的公钥
 * @returns Base64 编码的密文
 */
export function encryptWithPublicKey(data: string, publicKeyPem: string): string {
  const crypto = new RSACrypto();
  crypto.setPublicKeyFromPem(publicKeyPem);
  return crypto.encrypt(data);
}
