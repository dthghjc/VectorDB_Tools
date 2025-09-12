import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import apiKeysReducer from './slices/apiKeysSlice';
import milvusConnectionsReducer from './slices/milvusConnectionsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    apiKeys: apiKeysReducer,
    milvusConnections: milvusConnectionsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
