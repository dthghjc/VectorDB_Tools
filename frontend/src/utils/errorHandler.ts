import i18n from '@/i18n';

/**
 * 错误处理工具类
 * 提供统一的错误信息国际化处理
 */
export class ErrorHandler {
  /**
   * 后端错误信息映射表
   * 将已知的后端英文错误信息映射到国际化翻译键
   */
  private static readonly ERROR_MAPPINGS = {
    // 登录相关错误
    'Incorrect email or password': 'errors.loginFailed',
    'Inactive user': 'errors.inactiveUser',
    // 注册相关错误
    'Email already registered': 'errors.emailExists',
  };

  /**
   * 将后端错误信息转换为国际化错误信息
   * @param backendMessage - 后端返回的错误信息
   * @returns 国际化的错误信息，如果没有映射则返回原信息
   */
  private static translateBackendError(backendMessage: string): string {
    const translationKey = this.ERROR_MAPPINGS[backendMessage as keyof typeof this.ERROR_MAPPINGS];
    
    if (translationKey) {
      return i18n.t(translationKey);
    }
    
    // 如果没有映射，返回原始后端信息
    return backendMessage;
  }

  /**
   * 获取登录错误信息
   * @param error - API错误对象
   * @returns 国际化的错误信息
   */
  static getLoginError(error: any): string {
    // 获取后端返回的错误信息
    const backendMessage = error.response?.data?.detail || error.response?.data?.message;
    
    if (backendMessage) {
      // 尝试将后端错误信息转换为国际化信息
      return this.translateBackendError(backendMessage);
    }
    
    // 网络错误处理
    if (!error.response) {
      return i18n.t('errors.networkError');
    }
    
    // 默认登录失败信息
    return i18n.t('errors.loginFailed');
  }
  
  /**
   * 获取注册错误信息
   * @param error - API错误对象
   * @returns 国际化的错误信息
   */
  static getRegisterError(error: any): string {
    // 获取后端返回的错误信息
    const backendMessage = error.response?.data?.detail || error.response?.data?.message;
    
    if (backendMessage) {
      // 尝试将后端错误信息转换为国际化信息
      return this.translateBackendError(backendMessage);
    }
    
    // 网络错误处理
    if (!error.response) {
      return i18n.t('errors.networkError');
    }
    
    // 默认注册失败信息
    return i18n.t('errors.registerFailed');
  }
}
