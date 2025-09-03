import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setAuthFromStorage, validateToken, getCurrentUser } from '@/store/slices/authSlice';

interface RequireAuthProps {
  children: ReactNode;
  /**
   * 是否允许访问
   * true: 需要已登录
   * false: 需要未登录（如登录页面）
   */
  allowed: boolean;
  /**
   * 重定向目标路径
   */
  redirectTo: string;
}

export default function RequireAuth({ children, allowed, redirectTo }: RequireAuthProps) {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const location = useLocation();
  const { isAuthenticated, token, user, isLoading } = useAppSelector(state => state.auth);

  useEffect(() => {
    // 组件挂载时，首先从localStorage恢复认证状态
    dispatch(setAuthFromStorage());
  }, [dispatch]);

  useEffect(() => {
    // 验证token有效性
    if (token) {
      dispatch(validateToken());
    }
  }, [dispatch, token]);

  useEffect(() => {
    // 如果有token但没有用户信息，获取用户信息
    if (isAuthenticated && token && !user && !isLoading) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, isAuthenticated, token, user, isLoading]);

  // 显示加载状态，直到认证状态确定
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
          <p className="text-sm text-muted-foreground">{t('auth.verifying')}</p>
        </div>
      </div>
    );
  }

  // 根据allowed参数和当前认证状态决定是否允许访问
  if (allowed && !isAuthenticated) {
    // 需要登录但未登录，重定向到登录页面，并保存当前路径
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  if (!allowed && isAuthenticated) {
    // 需要未登录但已登录，重定向到主页或指定页面
    return <Navigate to={redirectTo} replace />;
  }

  // 认证状态符合要求，渲染子组件
  return <>{children}</>;
}
