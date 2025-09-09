// src/main.tsx
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { Provider } from 'react-redux';
import { Toaster } from 'sonner';
import { store } from './store';
import { router } from './router';
import AuthProvider from './components/auth/AuthProvider';
import './index.css';

import './i18n';

ReactDOM.createRoot(document.getElementById('root')!).render(
  //<React.StrictMode>
    <Provider store={store}>
      <AuthProvider>
        <RouterProvider router={router} />
        <Toaster richColors position="bottom-right" />
      </AuthProvider>
    </Provider>
  //</React.StrictMode>
);