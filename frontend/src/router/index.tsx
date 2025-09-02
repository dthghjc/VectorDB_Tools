import { createBrowserRouter } from 'react-router-dom';
import { lazy } from 'react';

// 1. 导入您的两种布局组件（布局组件保持同步导入，因为它们是必需的）
import AppLayout from '@/components/layout/AppLayout';
import AuthLayout from '@/components/layout/AuthLayout';

// 2. 懒加载页面组件
const HomePage = lazy(() => import('@/pages/home'));
const LoginPage = lazy(() => import('@/pages/auth/LoginPage'));
const SignupPage = lazy(() => import('@/pages/auth/SignupPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));

// 配置中心页面（懒加载）
const ConfigPage = lazy(() => import('@/pages/config'));
const MilvusConfigPage = lazy(() => import('@/pages/config/milvus'));
const ApiKeysPage = lazy(() => import('@/pages/config/api-keys'));

// Schema 管理页面（懒加载）
const SchemaPage = lazy(() => import('@/pages/schema'));
const CreateSchemaPage = lazy(() => import('@/pages/schema/create'));

// 数据导入页面（懒加载）
const DataImportPage = lazy(() => import('@/pages/data-import'));

// 任务中心页面（懒加载）
const TasksPage = lazy(() => import('@/pages/tasks'));

// 检索评估页面（懒加载）
const SearchEvalPage = lazy(() => import('@/pages/search-eval'));

// 3. 导入您的路由守卫（暂时注释，未来可能使用）
// import RequireAuth from '@/utils/RequireAuth';

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
        // 配置中心路由
        {
          path: '/config',
          element: <ConfigPage />,
        },
        {
          path: '/config/milvus',
          element: <MilvusConfigPage />,
        },
        {
          path: '/config/api-keys',
          element: <ApiKeysPage />,
        },
        // Schema 管理路由
        {
          path: '/schema',
          element: <SchemaPage />,
        },
        {
          path: '/schema/create',
          element: <CreateSchemaPage />,
        },
        // 数据导入路由
        {
          path: '/data-import',
          element: <DataImportPage />,
        },
        // 任务中心路由
        {
          path: '/tasks',
          element: <TasksPage />,
        },
        // 检索评估路由
        {
          path: '/search-eval',
          element: <SearchEvalPage />,
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