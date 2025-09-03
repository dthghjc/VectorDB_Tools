// src/main.tsx
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import { router } from './router';
import AuthProvider from './components/auth/AuthProvider';
import './index.css';

import './i18n';

// 移除LoadingFallback，统一使用shadcn表单组件的loading实现

ReactDOM.createRoot(document.getElementById('root')!).render(
  //<React.StrictMode>
    <Provider store={store}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </Provider>
  //</React.StrictMode>
);