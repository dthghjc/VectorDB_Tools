import { createBrowserRouter } from 'react-router-dom';

// 1. 导入您的两种布局组件
import AppLayout from '@/components/layout/AppLayout';
import AuthLayout from '@/components/layout/AuthLayout';

// 2. 导入您的所有页面组件
import HomePage from '@/pages/home';
import LoginPage from '@/pages/auth/LoginPage';
import SignupPage from '@/pages/auth/SignupPage';
import NotFoundPage from '@/pages/NotFoundPage';

// 3. 导入您的路由守卫
import RequireAuth from '@/utils/RequireAuth';

export const router = createBrowserRouter(
  [
    // 路由组 1: 应用主路由 (需要登录)
    {
      element: <AppLayout />, // 使用 AppLayout 作为这个组的布局
      errorElement: <NotFoundPage />,
      children: [
        {
          path: '/',
          // element: <RequireAuth allowed={true} redirectTo="/login"><HomePage /></RequireAuth>,
          element: <HomePage />,
        },
        // ...未来所有需要登录的页面都放在这里
      ],
    },

    // 路由组 2: 认证路由 (不能是登录状态)
    {
      element: <AuthLayout />, // 使用 AuthLayout 作为这个组的布局
      errorElement: <NotFoundPage />,
      children: [
        {
          path: '/login',
          // element: <RequireAuth allowed={false} redirectTo="/"><LoginPage /></RequireAuth>,
          element: <LoginPage />,
        },
        {
          path: '/signup',
          // element: <RequireAuth allowed={false} redirectTo="/"><SignupPage /></RequireAuth>,
          element: <SignupPage />,
        },
        // ...未来所有认证相关的页面都放在这里
      ],
    },

    // 顶层的 404 页面
    {
      path: '*',
      element: <NotFoundPage />,
    },
  ],
  {
    // 您的 vite.config.ts 中没有 base，所以这里的 basename 设置是正确的
    basename: import.meta.env.BASE_URL,
  }
);