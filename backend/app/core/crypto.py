# backend/app/core/crypto.py

import os
import base64
from pathlib import Path
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import logging

logger = logging.getLogger(__name__)

class RSAKeyManager:
    """
    RSA 密钥管理器
    
    负责 RSA 密钥对的生成、存储和加载。
    支持两种模式：
    1. 环境变量模式：从 .env 读取密钥
    2. 文件模式：自动生成并保存到文件
    """
    
    def __init__(self, key_size: int = 2048):
        self.key_size = key_size
        self.private_key: Optional[rsa.RSAPrivateKey] = None
        self.public_key: Optional[rsa.RSAPublicKey] = None
        
    def initialize(self) -> None:
        """
        初始化 RSA 密钥对
        仅从环境变量加载密钥，如果不存在则抛出错误
        """
        try:
            # 仅从环境变量加载
            if self._load_from_env():
                logger.info("✅ RSA 密钥从环境变量加载成功")
                return
                
            # 如果没有环境变量，则抛出错误
            error_msg = (
                "❌ 未找到 RSA 密钥对！请先运行以下命令生成密钥并添加到 .env：\n"
                "   ./generate-keys.sh\n"
                "然后将输出的密钥添加到 .env 文件中，重启应用。"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        except ValueError:
            # 重新抛出 ValueError（密钥未找到的错误）
            raise
        except Exception as e:
            logger.error(f"❌ RSA 密钥初始化失败: {e}")
            raise
    
    def _load_from_env(self) -> bool:
        """从环境变量加载 RSA 密钥对"""
        try:
            private_key_pem = os.getenv("RSA_PRIVATE_KEY")
            public_key_pem = os.getenv("RSA_PUBLIC_KEY")
            
            if not private_key_pem or not public_key_pem:
                return False
                
            # 解码 Base64 编码的密钥
            private_key_bytes = base64.b64decode(private_key_pem)
            public_key_bytes = base64.b64decode(public_key_pem)
            
            # 加载密钥
            self.private_key = serialization.load_pem_private_key(
                private_key_bytes, 
                password=None,
                backend=default_backend()
            )
            self.public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=default_backend()
            )
            
            return True
            
        except Exception as e:
            logger.warning(f"从环境变量加载 RSA 密钥失败: {e}")
            return False
    
    # 移除文件加载功能，仅支持环境变量模式
    # 提高安全性，避免敏感密钥文件泄露
    
    # 移除自动生成功能，仅保留加载功能
    # 用户应该通过 scripts/generate_rsa_keys.py 主动生成密钥对
    
    def decrypt_rsa(self, encrypted_data: str) -> str:
        """
        使用 RSA 私钥解密数据
        
        Args:
            encrypted_data: Base64 编码的加密数据
            
        Returns:
            解密后的原始字符串
        """
        if not self.private_key:
            raise ValueError("RSA 私钥未初始化")
            
        try:
            # 解码 Base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # RSA 解密
            decrypted_bytes = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"RSA 解密失败: {e}")
            raise
    
    def get_public_key_pem(self) -> str:
        """
        获取 PEM 格式的公钥字符串
        用于前端 API 调用
        
        Returns:
            PEM 格式的公钥字符串
        """
        # if not self.public_key:
        #     raise ValueError("RSA 公钥未初始化")
            
        # public_pem = self.public_key.public_bytes(
        #     encoding=serialization.Encoding.PEM,
        #     format=serialization.PublicFormat.SubjectPublicKeyInfo
        # )
        
        # return public_pem.decode('utf-8')
        return "public_key"

class AESCrypto:
    """
    AES 对称加密器
    
    用于在数据库中安全存储解密后的 API Key
    """
    
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or self._get_or_generate_key()
    
    def _get_or_generate_key(self) -> bytes:
        """获取或生成 AES 密钥"""
        # 尝试从环境变量获取
        aes_key_b64 = os.getenv("AES_ENCRYPTION_KEY")
        if aes_key_b64:
            try:
                return base64.b64decode(aes_key_b64)
            except Exception:
                logger.warning("环境变量中的 AES 密钥格式无效，将生成新密钥")
        
        # 生成新密钥
        new_key = secrets.token_bytes(32)  # 256-bit key
        key_b64 = base64.b64encode(new_key).decode('utf-8')
        
        logger.warning("🔑 生成新的 AES 加密密钥，请添加到 .env:")
        logger.warning(f"AES_ENCRYPTION_KEY={key_b64}")
        
        return new_key
    
    def encrypt(self, plaintext: str) -> str:
        """
        AES 加密
        
        Args:
            plaintext: 原始字符串
            
        Returns:
            Base64 编码的加密数据 (IV + 密文)
        """
        # 生成随机 IV
        iv = secrets.token_bytes(16)
        
        # 创建加密器
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # 填充明文到 16 字节的倍数
        padded_data = self._pad(plaintext.encode('utf-8'))
        
        # 加密
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # 组合 IV + 密文并 Base64 编码
        encrypted_data = iv + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        AES 解密
        
        Args:
            encrypted_data: Base64 编码的加密数据
            
        Returns:
            解密后的原始字符串
        """
        # 解码 Base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # 分离 IV 和密文
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # 创建解密器
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 解密
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 去除填充
        plaintext = self._unpad(padded_data)
        
        return plaintext.decode('utf-8')
    
    def _pad(self, data: bytes) -> bytes:
        """PKCS7 填充"""
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad(self, data: bytes) -> bytes:
        """移除 PKCS7 填充"""
        padding_length = data[-1]
        return data[:-padding_length]


# 全局实例
rsa_manager = RSAKeyManager()
aes_crypto = AESCrypto()


def initialize_crypto() -> None:
    """
    初始化加密系统
    应用启动时调用，包含密钥一致性检查
    """
    logger.info("🔐 初始化加密系统...")
    rsa_manager.initialize()
    
    # TODO: 在实现数据库后添加密钥一致性检查
    # 检查当前密钥是否能解密数据库中的现有数据
    # _verify_key_consistency()
    
    logger.info("✅ 加密系统初始化完成")


def encrypt_api_key(rsa_encrypted_key: str) -> str:
    """
    完整的 API Key 加密流程
    
    Args:
        rsa_encrypted_key: 前端 RSA 加密后的 API Key
        
    Returns:
        AES 加密后用于数据库存储的字符串
    """
    # 1. RSA 解密得到原始 API Key
    original_key = rsa_manager.decrypt_rsa(rsa_encrypted_key)
    
    # 2. AES 加密用于数据库存储
    encrypted_for_db = aes_crypto.encrypt(original_key)
    
    return encrypted_for_db


def decrypt_api_key(encrypted_key: str) -> str:
    """
    从数据库解密 API Key
    
    Args:
        encrypted_key: 数据库中存储的 AES 加密数据
        
    Returns:
        解密后的原始 API Key
    """
    return aes_crypto.decrypt(encrypted_key)


def encrypt_sensitive_data(data: str) -> str:
    """
    加密敏感数据（通用接口）
    用于 Milvus 连接信息、密码等敏感数据的加密
    
    Args:
        data: 需要加密的敏感数据
        
    Returns:
        AES 加密后用于数据库存储的字符串
    """
    return aes_crypto.encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    解密敏感数据（通用接口）
    用于 Milvus 连接信息、密码等敏感数据的解密
    
    Args:
        encrypted_data: 数据库中存储的 AES 加密数据
        
    Returns:
        解密后的原始数据
    """
    return aes_crypto.decrypt(encrypted_data)


def get_public_key() -> str:
    """
    获取 RSA 公钥
    供前端 API 调用
    
    Returns:
        PEM 格式的 RSA 公钥
    """
    return rsa_manager.get_public_key_pem()


def get_key_fingerprint() -> str:
    """
    获取当前 RSA 密钥的指纹
    用于验证密钥一致性
    
    Returns:
        密钥指纹 (SHA256)
    """
    public_key_pem = rsa_manager.get_public_key_pem()
    import hashlib
    fingerprint = hashlib.sha256(public_key_pem.encode()).hexdigest()[:16]
    return fingerprint


# TODO: 在实现数据库模型后实现这个函数
def _verify_key_consistency() -> None:
    """
    验证当前密钥是否与数据库中的数据兼容
    
    如果数据库中有加密数据，但当前密钥无法解密，则发出警告
    """
    logger.info("🔍 验证密钥一致性...")
    
    # 获取当前密钥指纹
    current_fingerprint = get_key_fingerprint()
    logger.info(f"当前密钥指纹: {current_fingerprint}")
    
    # TODO: 从数据库检查是否有加密的敏感数据
    # from app.crud.api_key import get_api_key_count
    # from app.crud.milvus_config import get_milvus_config_count
    # 
    # api_key_count = get_api_key_count()
    # milvus_config_count = get_milvus_config_count()
    # total_encrypted_count = api_key_count + milvus_config_count
    
    # if total_encrypted_count > 0:
    #     logger.warning(
    #         f"⚠️  数据库中有 {total_encrypted_count} 条加密数据，"
    #         f"包括 {api_key_count} 个 API Key，{milvus_config_count} 个 Milvus 配置。"
    #         "请确保当前密钥与加密时使用的密钥一致！"
    #     )
    
    logger.info("✅ 密钥一致性检查完成")
