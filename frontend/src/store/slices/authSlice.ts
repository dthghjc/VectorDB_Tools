import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { jwtDecode } from 'jwt-decode';
import { authService } from '@/services/api/auth';

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface TokenPayload {
  sub: string; // email
  user_id: string;
  exp: number;
  iat: number;
}

// Initial state
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      console.log('Auth slice: attempting login with:', credentials.email);
      const response = await authService.login(credentials);
      console.log('Auth slice: login successful:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Auth slice: login failed:', error.response?.data || error.message);
      return rejectWithValue(
        error.response?.data?.detail || 'Login failed'
      );
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authService.getCurrentUser();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to get user info'
      );
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logoutUser',
  async () => {
    // 清除本地存储的token
    localStorage.removeItem('access_token');
    return null;
  }
);

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    // 验证token有效性
    validateToken: (state) => {
      if (state.token) {
        try {
          const decoded = jwtDecode<TokenPayload>(state.token);
          const currentTime = Date.now() / 1000;
          
          if (decoded.exp < currentTime) {
            // Token已过期
            state.token = null;
            state.user = null;
            state.isAuthenticated = false;
            localStorage.removeItem('access_token');
          } else {
            state.isAuthenticated = true;
          }
        } catch (error) {
          // Token无效
          state.token = null;
          state.user = null;
          state.isAuthenticated = false;
          localStorage.removeItem('access_token');
        }
      }
    },
    // 手动设置认证状态（用于初始化时从localStorage恢复）
    setAuthFromStorage: (state) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const decoded = jwtDecode<TokenPayload>(token);
          const currentTime = Date.now() / 1000;
          
          if (decoded.exp > currentTime) {
            state.token = token;
            state.isAuthenticated = true;
          } else {
            localStorage.removeItem('access_token');
          }
        } catch (error) {
          localStorage.removeItem('access_token');
        }
      }
    }
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
        state.error = null;
        // 保存token到localStorage
        localStorage.setItem('access_token', action.payload.access_token);
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
        state.token = null;
        state.user = null;
      })
      // Get current user
      .addCase(getCurrentUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        // 如果获取用户信息失败，可能token已失效
        state.isAuthenticated = false;
        state.token = null;
        state.user = null;
        localStorage.removeItem('access_token');
      })
      // Logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = null;
        state.isLoading = false;
      });
  },
});

export const { clearError, validateToken, setAuthFromStorage } = authSlice.actions;
export default authSlice.reducer;
