import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import apiKeysReducer from './slices/apiKeysSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    apiKeys: apiKeysReducer,
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
