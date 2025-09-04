#!/bin/bash
# RSA 密钥对生成脚本 (安全版本)
# 使用系统自带的 openssl 工具，仅输出环境变量格式

set -e

echo "🔑 生成 RSA 密钥对..."

# 检查 openssl 是否可用
if ! command -v openssl &> /dev/null; then
    echo "❌ 错误：未找到 openssl 工具"
    echo "   请安装 openssl：sudo apt install openssl (Ubuntu/Debian)"
    echo "   或：brew install openssl (macOS)"
    exit 1
fi

# 创建临时文件
TEMP_DIR=$(mktemp -d)
PRIVATE_KEY="$TEMP_DIR/rsa_private.pem"
PUBLIC_KEY="$TEMP_DIR/rsa_public.pem"

# 清理函数
cleanup() {
    echo "🧹 清理临时文件..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# 生成私钥 (2048 位)
echo "📝 生成私钥..."
openssl genrsa -out "$PRIVATE_KEY" 2048 2>/dev/null

# 从私钥提取公钥
echo "📝 生成公钥..."
openssl rsa -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY" 2>/dev/null

# 生成 AES 加密密钥 (256-bit)
echo "📝 生成 AES 加密密钥..."
AES_KEY=$(openssl rand -base64 32)

# 生成 Base64 编码的 RSA 密钥（用于环境变量）
echo "📝 生成环境变量格式..."
PRIVATE_B64=$(base64 -w 0 "$PRIVATE_KEY")
PUBLIC_B64=$(base64 -w 0 "$PUBLIC_KEY")

echo ""
echo "✅ 所有密钥生成完成！"
echo ""
echo "🔧 请将以下内容添加到后端的 .env 文件:"
echo "***********************************************************************"
echo "RSA_PRIVATE_KEY=\"$PRIVATE_B64\""
echo "RSA_PUBLIC_KEY=\"$PUBLIC_B64\""
echo "AES_ENCRYPTION_KEY=\"$AES_KEY\""
echo "***********************************************************************"
echo ""
echo "💡 使用方法:"
echo "   1. 复制上面的三行到 backend/.env 文件"
echo "   2. 如果没有 .env 文件，请在 backend 目录下创建一个"
echo ""
echo "🔒 安全特性:"
echo "   - 不保存密钥文件到磁盘"
echo "   - 临时文件已自动清理"
echo "   - 仅通过环境变量传递密钥"
echo ""
echo "⚠️  安全提醒:"
echo "   - 请妥善保管 backend/.env 文件，不要提交到版本控制"
echo "   - ⚠️  密钥轮换风险：更换任何密钥会导致数据库中所有已加密的数据无法解密！"
echo "   - 如需轮换密钥，请先备份并重新加密所有现有的敏感数据"
