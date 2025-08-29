import React from 'react';
import ReactDOM from 'react-dom/client';
// 1. 从 react-router-dom 导入 RouterProvider 组件
import { RouterProvider } from 'react-router-dom';

// 2. 导入您在 `src/router` 文件夹中创建并导出的 router 实例
import { router } from './router'; // 确保这个路径指向您的 router/index.tsx

// 3. 导入您的全局样式文件
import './index.css';

// 4. 获取 DOM 根节点并渲染应用
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* 5. 在这里使用 RouterProvider!
      这将启动您在 router/index.tsx 中定义的所有路由规则。
      这是让所有路由和布局生效的最后一步，也是最关键的一步。
    */}
    <RouterProvider router={router} />
  </React.StrictMode>
);

