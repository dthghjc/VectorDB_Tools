// src/main.tsx
import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import './index.css';

import './i18n';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* 2. 使用 React Suspense 作为 fallback UI，
        主要用于处理国际化文件的异步加载。
        页面级别的懒加载在 AppLayout 内处理。
    */}
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">正在初始化...</p>
        </div>
      </div>
    }>
      <RouterProvider router={router} />
    </Suspense>
  </React.StrictMode>
);