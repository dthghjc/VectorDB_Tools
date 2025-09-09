import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '@/store/hooks';

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
  const location = useLocation();
  const { isAuthenticated, isInitialized } = useAppSelector(state => state.auth);

  // 如果认证状态尚未初始化，显示加载状态而不是重定向
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">正在验证身份...</p>
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
