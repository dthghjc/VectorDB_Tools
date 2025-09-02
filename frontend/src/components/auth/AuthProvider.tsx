import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setAuthFromStorage, validateToken, logoutUser } from '@/store/slices/authSlice';

interface AuthProviderProps {
  children: ReactNode;
}

interface TokenPayload {
  sub: string;
  user_id: string;
  exp: number;
  iat: number;
}

/**
 * 认证提供者组件
 * 负责应用启动时的认证初始化和自动token验证
 */
export default function AuthProvider({ children }: AuthProviderProps) {
  const dispatch = useAppDispatch();
  const { token, isAuthenticated } = useAppSelector(state => state.auth);
  const tokenCheckInterval = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // 应用启动时初始化认证状态
    dispatch(setAuthFromStorage());
    dispatch(validateToken());
  }, [dispatch]);

  useEffect(() => {
    // 设置token定期检查
    const checkTokenExpiry = () => {
      if (token && isAuthenticated) {
        try {
          const decoded = jwtDecode<TokenPayload>(token);
          const currentTime = Date.now() / 1000;
          const timeUntilExpiry = decoded.exp - currentTime;
          
          // 如果token将在5分钟内过期，提前登出
          if (timeUntilExpiry <= 300) {
            console.warn('Token将要过期，自动登出');
            dispatch(logoutUser());
          }
        } catch (error) {
          console.error('Token解析错误:', error);
          dispatch(logoutUser());
        }
      }
    };

    // 每30秒检查一次token状态
    if (isAuthenticated && token) {
      tokenCheckInterval.current = setInterval(checkTokenExpiry, 30000);
      // 立即检查一次
      checkTokenExpiry();
    } else {
      // 清除定时器如果用户未登录
      if (tokenCheckInterval.current) {
        clearInterval(tokenCheckInterval.current);
        tokenCheckInterval.current = null;
      }
    }

    // 清理函数
    return () => {
      if (tokenCheckInterval.current) {
        clearInterval(tokenCheckInterval.current);
      }
    };
  }, [dispatch, token, isAuthenticated]);

  // 监听token变化，当token失效时清理定时器
  useEffect(() => {
    if (!token || !isAuthenticated) {
      if (tokenCheckInterval.current) {
        clearInterval(tokenCheckInterval.current);
        tokenCheckInterval.current = null;
      }
    }
  }, [token, isAuthenticated]);

  return <>{children}</>;
}
