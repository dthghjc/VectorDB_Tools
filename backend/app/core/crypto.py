# backend/app/core/crypto.py

import base64
from typing import Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class RSAKeyManager:
    """
    RSA 密钥管理器
    
    负责从环境变量加载 RSA 密钥对，用于前端传输的 API Key 解密。
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
        """从统一配置加载 RSA 密钥对"""
        try:
            private_key_pem = settings.RSA_PRIVATE_KEY
            public_key_pem = settings.RSA_PUBLIC_KEY
            
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
            logger.warning(f"从配置加载 RSA 密钥失败: {e}")
            return False
    
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
        if not self.public_key:
            raise ValueError("RSA 公钥未初始化")
            
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return public_pem.decode('utf-8')

class AESCrypto:
    """
    AES 对称加密器
    
    用于在数据库中安全存储解密后的 API Key
    """
    
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or self._get_key_from_config()
    
    def _get_key_from_config(self) -> bytes:
        """从配置获取 AES 密钥"""
        aes_key_b64 = settings.AES_ENCRYPTION_KEY
        if not aes_key_b64:
            raise ValueError("AES_ENCRYPTION_KEY 未配置！请运行 ./generate-keys.sh 生成密钥")
            
        try:
            return base64.b64decode(aes_key_b64)
        except Exception as e:
            raise ValueError(f"AES_ENCRYPTION_KEY 格式无效: {e}")
    
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


# 全局实例（延迟初始化）
rsa_manager: Optional[RSAKeyManager] = None
aes_crypto: Optional[AESCrypto] = None


def initialize_crypto() -> None:
    """
    初始化加密系统
    应用启动时调用
    """
    global rsa_manager, aes_crypto
    
    logger.info("🔐 初始化加密系统...")
    
    # 初始化 RSA 管理器
    rsa_manager = RSAKeyManager()
    rsa_manager.initialize()
    
    # 初始化 AES 加密器
    aes_crypto = AESCrypto()
    
    logger.info("✅ 加密系统初始化完成")


def encrypt_api_key(rsa_encrypted_key: str) -> str:
    """
    完整的 API Key 加密流程
    
    Args:
        rsa_encrypted_key: 前端 RSA 加密后的 API Key
        
    Returns:
        AES 加密后用于数据库存储的字符串
    """
    if not rsa_manager or not aes_crypto:
        raise RuntimeError("加密系统未初始化，请先调用 initialize_crypto()")
        
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
    if not aes_crypto:
        raise RuntimeError("加密系统未初始化，请先调用 initialize_crypto()")
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
    if not aes_crypto:
        raise RuntimeError("加密系统未初始化，请先调用 initialize_crypto()")
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
    if not aes_crypto:
        raise RuntimeError("加密系统未初始化，请先调用 initialize_crypto()")
    return aes_crypto.decrypt(encrypted_data)


def get_public_key() -> str:
    """
    获取 RSA 公钥
    供前端 API 调用
    
    Returns:
        PEM 格式的 RSA 公钥
    """
    if not rsa_manager:
        raise RuntimeError("加密系统未初始化，请先调用 initialize_crypto()")
    return rsa_manager.get_public_key_pem()
