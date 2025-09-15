import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { jwtDecode } from 'jwt-decode';
import { authService } from '@/services/api/auth';
import { ErrorHandler } from '@/utils/errorHandler';

// ============================
// 类型定义 (Type Definitions)
// ============================

/**
 * 用户信息接口
 * 只包含前端UI需要的用户基本信息
 */
export interface User {
  email: string;              // 用户邮箱地址
  full_name: string | null;   // 用户全名（可为空）
}

/**
 * 认证状态接口
 * 管理用户的登录状态和相关信息
 */
export interface AuthState {
  user: User | null;          // 当前登录用户信息
  token: string | null;       // JWT访问令牌
  isAuthenticated: boolean;   // 是否已认证
  isInitialized: boolean;     // 认证状态是否已初始化（防止刷新时误重定向）
  isLoading: boolean;         // 是否正在加载（登录/注册/获取用户信息等）
  error: string | null;       // 错误信息
}

/**
 * 登录凭证接口
 * 用户登录时需要提供的信息
 */
interface LoginCredentials {
  email: string;              // 邮箱地址
  password: string;           // 密码
}

/**
 * 注册凭证接口
 * 用户注册时需要提供的信息
 */
interface RegisterCredentials {
  email: string;              // 邮箱地址
  full_name: string;          // 全名
  password: string;           // 密码
}

/**
 * JWT Token载荷接口
 * 解码JWT token后的数据结构
 */
interface TokenPayload {
  sub: string;                // 主题（通常是邮箱）
  user_id: string;            // 用户ID
  exp: number;                // 过期时间戳
  iat: number;                // 签发时间戳
}

// ============================
// 工具函数 (Utility Functions)
// ============================

/**
 * 本地存储管理器
 * 统一管理localStorage中的认证数据操作
 */
const storageManager = {
  // 获取存储的token
  getToken: (): string | null => localStorage.getItem('access_token'),
  
  // 保存token到本地存储
  setToken: (token: string): void => {
    localStorage.setItem('access_token', token);
  },
  
  // 获取存储的用户信息
  getUser: (): User | null => {
    const userStr = localStorage.getItem('user_info');
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      return null;
    }
  },
  
  // 保存用户信息到本地存储
  setUser: (user: User): void => {
    localStorage.setItem('user_info', JSON.stringify(user));
  },
  
  // 清除所有认证数据
  clear: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
  }
};

/**
 * Token验证器
 * 统一的token有效性验证逻辑
 */
const tokenValidator = {
  /**
   * 验证token是否有效
   * @param token - JWT token字符串
   * @returns 验证结果和解码后的payload
   */
  validate: (token: string | null): { isValid: boolean; payload?: TokenPayload } => {
    if (!token) {
      return { isValid: false };
    }

    try {
      const decoded = jwtDecode<TokenPayload>(token);
      const currentTime = Date.now() / 1000;
      
      // 检查token是否过期
      if (decoded.exp < currentTime) {
        return { isValid: false };
      }
      
      return { isValid: true, payload: decoded };
    } catch (error) {
      // token格式无效
      return { isValid: false };
    }
  }
};

/**
 * 状态清理器
 * 统一的认证状态清理逻辑
 */
const authStateResetter = {
  /**
   * 清理认证状态并移除本地存储
   * @param state - 当前的认证状态
   */
  clearAuthState: (state: AuthState): void => {
    state.token = null;
    state.user = null;
    state.isAuthenticated = false;
    storageManager.clear();
  }
};

// ============================
// 初始状态 (Initial State)
// ============================

/**
 * 认证模块的初始状态
 * 保持纯净的初始状态，token恢复在AuthProvider中通过setAuthFromStorage完成
 */
const initialState: AuthState = {
  user: null,                                    // 初始无用户信息
  token: null,                                   // 初始无token（将通过setAuthFromStorage恢复）
  isAuthenticated: false,                        // 初始未认证状态
  isInitialized: false,                          // 初始未初始化状态
  isLoading: false,                              // 初始无加载状态
  error: null,                                   // 初始无错误
};

// ============================
// 异步操作 (Async Thunks)
// ============================

/**
 * 用户登录异步操作
 * 处理用户登录流程，包括API调用和错误处理
 */
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      
      // 调用登录API
      const response = await authService.login(credentials);
      
      
      return response.data;
    } catch (error: any) {
      
      // 使用错误处理工具获取国际化错误信息
      const errorMessage = ErrorHandler.getLoginError(error);
      
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * 用户注册异步操作
 * 处理用户注册流程，注册成功后不自动登录
 */
export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async (credentials: RegisterCredentials, { rejectWithValue }) => {
    try {
      
      // 调用注册API
      const response = await authService.register(credentials);
      
      return response.data;
    } catch (error: any) {
      
      // 使用错误处理工具获取国际化错误信息
      const errorMessage = ErrorHandler.getRegisterError(error);
      
      return rejectWithValue(errorMessage);
    }
  }
);

// 注意：不再需要getCurrentUser操作，登录时已获取所有必要信息
// 如果将来需要更新用户信息，可以添加updateUser操作

/**
 * 用户退出登录异步操作
 * 清除本地存储的认证信息
 */
export const logoutUser = createAsyncThunk(
  'auth/logoutUser',
  async () => {
    
    // 清除所有本地存储的认证数据
    storageManager.clear();
    
    return null;
  }
);

// ============================
// Redux Slice 定义
// ============================

/**
 * 认证状态管理切片
 * 使用Redux Toolkit的createSlice创建，包含同步reducers和异步extraReducers
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /**
     * 清除错误信息
     * 用于用户重新尝试操作前清除之前的错误状态
     */
    clearError: (state) => {
      state.error = null;
    },
    
    /**
     * 验证token有效性
     * 检查当前存储的token是否有效，无效则清除认证状态
     */
    validateToken: (state) => {
      
      if (!state.token) {
        return;
      }
      
      const { isValid } = tokenValidator.validate(state.token);
      
      if (isValid) {
        state.isAuthenticated = true;
      } else {
        authStateResetter.clearAuthState(state);
      }
    },
    
    /**
     * 从本地存储恢复认证状态
     * 应用启动时调用，用于恢复用户的登录状态
     */
    setAuthFromStorage: (state) => {
      
      const token = storageManager.getToken();
      
      if (!token) {
        state.isInitialized = true;  // 标记初始化完成，即使没有token
        return;
      }
      
      const { isValid } = tokenValidator.validate(token);
      
      if (isValid) {
        state.token = token;
        state.isAuthenticated = true;
        state.isInitialized = true;  // 标记初始化完成
        
        // 同时恢复用户信息
        const user = storageManager.getUser();
        if (user) {
          state.user = user;
        }
      } else {
        storageManager.clear();
        state.isInitialized = true;  // 标记初始化完成，即使token无效
      }
    }
  },
  /**
   * 异步操作的状态处理
   * 处理createAsyncThunk创建的异步actions的各种状态
   */
  extraReducers: (builder) => {
    builder
      // ==================== 登录相关 ====================
      
      // 登录开始
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      
      // 登录成功
      .addCase(loginUser.fulfilled, (state, action) => {
        
        state.isLoading = false;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
        state.isInitialized = true;  // 登录成功后标记已初始化
        state.error = null;
        
        // 根据登录响应创建用户对象（包含所有需要的信息）
        // 注意：email在JWT和响应中重复，但为了代码简洁，直接使用响应数据
        state.user = {
          email: action.payload.email,
          full_name: action.payload.full_name
        };
        
        // 保存token和用户信息到本地存储
        storageManager.setToken(action.payload.access_token);
        storageManager.setUser(state.user!);
      })
      
      // 登录失败
      .addCase(loginUser.rejected, (state, action) => {
        
        state.isLoading = false;
        state.error = action.payload as string;
        
        // 清除认证状态
        authStateResetter.clearAuthState(state);
      })
      
      // 注意：不再需要getCurrentUser相关的状态处理
      // 登录成功后已包含所有必要的用户信息
      
      // ==================== 注册相关 ====================
      
      // 注册开始
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      
      // 注册成功
      .addCase(registerUser.fulfilled, (state, action) => {
        
        state.isLoading = false;
        state.user = action.payload;
        state.error = null;
        
        // 注意：注册成功后不自动登录，用户需要管理员审核或邮箱验证
        // 保持isAuthenticated为false
      })
      
      // 注册失败
      .addCase(registerUser.rejected, (state, action) => {
        
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // ==================== 退出登录相关 ====================
      
      // 退出登录成功
      .addCase(logoutUser.fulfilled, (state) => {
        
        // 重置所有认证相关状态，但保持已初始化状态
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = null;
        state.isLoading = false;
        // isInitialized 保持 true，因为认证系统已经初始化过了
      });
  },
});

// ============================
// 导出 (Exports)
// ============================

/**
 * 导出同步actions
 * 这些actions可以直接在组件中dispatch使用
 */
export const { 
  clearError,           // 清除错误信息
  validateToken,        // 验证token有效性
  setAuthFromStorage    // 从本地存储恢复认证状态
} = authSlice.actions;

/**
 * 导出reducer
 * 用于在store中注册auth状态管理
 */
export default authSlice.reducer;

// ============================
// 选择器 (Selectors)
// ============================

/**
 * 认证状态选择器
 * 提供便捷的状态选择函数，用于在组件中获取特定的认证状态
 */
export const authSelectors = {
  // 获取当前用户信息
  selectUser: (state: { auth: AuthState }) => state.auth.user,
  
  // 获取认证状态
  selectIsAuthenticated: (state: { auth: AuthState }) => state.auth.isAuthenticated,
  
  // 获取加载状态
  selectIsLoading: (state: { auth: AuthState }) => state.auth.isLoading,
  
  // 获取错误信息
  selectError: (state: { auth: AuthState }) => state.auth.error,
  
  // 获取token
  selectToken: (state: { auth: AuthState }) => state.auth.token,
  
  // 注意：移除了selectIsUserActive，因为前端不再需要is_active字段
  
  // 获取用户邮箱
  selectUserEmail: (state: { auth: AuthState }) => state.auth.user?.email,
  
  // 获取用户全名
  selectUserFullName: (state: { auth: AuthState }) => state.auth.user?.full_name
};
