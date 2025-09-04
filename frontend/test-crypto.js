// 测试 RSA 加密的简单脚本
const forge = require('node-forge');

// 从API获取的公钥
const publicKeyPem = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArws3GiHI1cPyPqi7SGMN
B9iSRUGnbqO8hj4hZHWGCpj+QZ7vs980cEtGq+wJ0zYYMUHviL9cK9duDwc/J62S
eEj3FumVt/7JFUa7OR2xxi2Ap6CUSexD2OrmmQ3gkOwOsuwJv79CiBgNHgglfjlo
kMLK/wNLoOMB174+YvImhTMPECJoARyYb5Gmnbvc5gXWG2QkgLEjw58XJhCWspOW
+HrNLaXsm0YHZM6eHDvbs4OWxKGb432OJa6mVhJHF2kDjImvqG9HERu4wN1v+/l4
0nzlSE9HNYlZuJ1Zev7whZ/RFGnFLLWpsk8Nvw4zj+kwzT34YmwswNa+mnmrS1pW
pwIDAQAB
-----END PUBLIC KEY-----`;

try {
  // 解析公钥
  const publicKey = forge.pki.publicKeyFromPem(publicKeyPem);
  console.log('✅ 公钥解析成功');

  // 测试数据
  const testData = 'sk-test-1234567890abcdef';
  console.log('📝 测试数据:', testData);

  // 测试不同的填充方式
  const paddingMethods = ['RSAES-PKCS1-V1_5', 'RSA-OAEP'];
  
  for (const padding of paddingMethods) {
    try {
      console.log(`\n🔐 测试填充方式: ${padding}`);
      const encrypted = publicKey.encrypt(testData, padding);
      const base64Encrypted = forge.util.encode64(encrypted);
      console.log('✅ 加密成功');
      console.log('📦 加密结果长度:', base64Encrypted.length);
      console.log('📦 加密结果前32字符:', base64Encrypted.substring(0, 32));
    } catch (error) {
      console.log(`❌ ${padding} 加密失败:`, error.message);
    }
  }

} catch (error) {
  console.log('❌ 错误:', error.message);
}
