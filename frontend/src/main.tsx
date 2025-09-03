// src/main.tsx
import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { Provider } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { store } from './store';
import { router } from './router';
import AuthProvider from './components/auth/AuthProvider';
import './index.css';

import './i18n';

function LoadingFallback() {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-muted-foreground">{t('auth.loading')}</p>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  //<React.StrictMode>
    <Provider store={store}>
      <AuthProvider>
        <Suspense fallback={<LoadingFallback />}>
          <RouterProvider router={router} />
        </Suspense>
      </AuthProvider>
    </Provider>
  //</React.StrictMode>
);