import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpApi from 'i18next-http-backend';

i18n
  // 使用 i18next-http-backend 从服务器/public文件夹加载翻译文件
  .use(HttpApi)
  // 检测用户语言
  .use(LanguageDetector)
  // 将 i18n 实例传递给 react-i18next
  .use(initReactI18next)
  // 初始化 i18next
  .init({
    // 默认语言
    fallbackLng: 'zh',
    // 支持的语言列表
    supportedLngs: ['en', 'zh'],
    debug: true, // 在开发模式下开启 debug
    
    detection: {
      // 配置语言检测器
      order: ['queryString', 'cookie', 'localStorage', 'navigator', 'htmlTag'],
      caches: ['cookie'],
    },

    interpolation: {
      escapeValue: false, // React 已经可以防止 XSS
    },

    backend: {
      // 翻译文件的路径
      loadPath: '/locales/{{lng}}/translation.json',
    },
  });

export default i18n;