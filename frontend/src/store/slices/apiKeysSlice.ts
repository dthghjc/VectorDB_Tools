import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { apiKeyService } from '@/services/api/apiKeys';
import type { 
  ApiKey, 
  CreateApiKeyRequest
} from '@/types/apiKeys';

/**
 * API Key 状态接口
 */
interface ApiKeysState {
  // 数据状态
  items: ApiKey[];
  currentItem: ApiKey | null;
  
  // 分页状态
  total: number;
  page: number;
  size: number;
  
  // 加载状态
  loading: {
    list: boolean;
    create: boolean;
    update: Record<string, boolean>; // 以 ID 为键的更新状态
    delete: Record<string, boolean>; // 以 ID 为键的删除状态
    test: Record<string, boolean>; // 以 ID 为键的测试状态
  };
  
  // 错误状态
  error: {
    list: string | null;
    create: string | null;
    update: Record<string, string | null>; // 以 ID 为键的更新错误
    delete: Record<string, string | null>; // 以 ID 为键的删除错误
    test: Record<string, string | null>; // 以 ID 为键的测试错误
  };
  
  // 统计信息
  stats: {
    total: number;
    active: number;
    inactive: number;
    by_provider: Record<string, number>;
  } | null;
}

/**
 * 初始状态
 */
const initialState: ApiKeysState = {
  items: [],
  currentItem: null,
  total: 0,
  page: 1,
  size: 10,
  loading: {
    list: false,
    create: false,
    update: {},
    delete: {},
    test: {},
  },
  error: {
    list: null,
    create: null,
    update: {},
    delete: {},
    test: {},
  },
  stats: null,
};

/**
 * 异步 Action：创建 API Key
 */
export const createApiKey = createAsyncThunk(
  'apiKeys/create',
  async (data: CreateApiKeyRequest, { rejectWithValue }) => {
    try {
      const response = await apiKeyService.create(data);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '创建失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：获取 API Key 列表
 */
export const fetchApiKeys = createAsyncThunk(
  'apiKeys/fetchList',
  async ({ page = 1, size = 10 }: { page?: number; size?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await apiKeyService.getList(page, size);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '获取列表失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：获取单个 API Key
 */
export const fetchApiKeyById = createAsyncThunk(
  'apiKeys/fetchById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await apiKeyService.getById(id);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '获取详情失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：更新 API Key
 */
export const updateApiKey = createAsyncThunk(
  'apiKeys/update',
  async ({ id, data }: { id: string; data: { name?: string; provider?: string; base_url?: string; status?: 'active' | 'inactive' } }, { rejectWithValue }) => {
    try {
      const response = await apiKeyService.update(id, data);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '更新失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：删除 API Key
 */
export const deleteApiKey = createAsyncThunk(
  'apiKeys/delete',
  async (id: string, { rejectWithValue }) => {
    try {
      await apiKeyService.delete(id);
      return id;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '删除失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：获取统计信息
 */
export const fetchApiKeyStats = createAsyncThunk(
  'apiKeys/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiKeyService.getStats();
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '获取统计失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 测试 API Key
 */
export const testApiKey = createAsyncThunk(
  'apiKeys/test',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await apiKeyService.test(id);
      return { id, ...response };
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'API Key 测试失败';
      return rejectWithValue({ id, message });
    }
  }
);

/**
 * API Keys Slice
 */
const apiKeysSlice = createSlice({
  name: 'apiKeys',
  initialState,
  reducers: {
    // 清除特定错误
    clearError: (state, action: PayloadAction<keyof ApiKeysState['error']>) => {
      const key = action.payload;
      if (key === 'test') {
        state.error.test = {};
      } else {
        (state.error as any)[key] = null;
      }
    },
    
    // 清除所有错误
    clearAllErrors: (state) => {
      state.error = {
        list: null,
        create: null,
        update: {},
        delete: {},
        test: {},
      };
    },
    
    // 重置状态
    resetState: () => initialState,
    
    // 设置当前项
    setCurrentItem: (state, action: PayloadAction<ApiKey | null>) => {
      state.currentItem = action.payload;
    },
  },
  extraReducers: (builder) => {
    // 创建 API Key
    builder
      .addCase(createApiKey.pending, (state) => {
        state.loading.create = true;
        state.error.create = null;
      })
      .addCase(createApiKey.fulfilled, (state, action) => {
        state.loading.create = false;
        // 将新创建的项添加到列表开头
        const newItem: ApiKey = {
          ...action.payload,
          last_used_at: null, // 新创建的密钥从未使用
          last_tested_at: null,
          test_status: null,
          test_message: null,
          test_response_time: null,
        };
        state.items.unshift(newItem);
        state.total += 1;
      })
      .addCase(createApiKey.rejected, (state, action) => {
        state.loading.create = false;
        state.error.create = action.payload as string;
      });

    // 获取列表
    builder
      .addCase(fetchApiKeys.pending, (state) => {
        state.loading.list = true;
        state.error.list = null;
      })
      .addCase(fetchApiKeys.fulfilled, (state, action) => {
        state.loading.list = false;
        state.items = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.size = action.payload.size;
      })
      .addCase(fetchApiKeys.rejected, (state, action) => {
        state.loading.list = false;
        state.error.list = action.payload as string;
      });

    // 获取单个详情
    builder
      .addCase(fetchApiKeyById.fulfilled, (state, action) => {
        state.currentItem = action.payload;
      });

    // 更新 API Key
    builder
      .addCase(updateApiKey.pending, (state, action) => {
        const apiKeyId = action.meta.arg.id;
        state.loading.update[apiKeyId] = true;
        delete state.error.update[apiKeyId];
      })
      .addCase(updateApiKey.fulfilled, (state, action) => {
        const apiKeyId = action.payload.id;
        delete state.loading.update[apiKeyId];
        // 更新列表中的对应项
        const index = state.items.findIndex(item => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        // 更新当前项
        if (state.currentItem?.id === action.payload.id) {
          state.currentItem = action.payload;
        }
      })
      .addCase(updateApiKey.rejected, (state, action) => {
        const apiKeyId = action.meta.arg.id;
        delete state.loading.update[apiKeyId];
        state.error.update[apiKeyId] = action.payload as string;
      });

    // 删除 API Key
    builder
      .addCase(deleteApiKey.pending, (state, action) => {
        const apiKeyId = action.meta.arg;
        state.loading.delete[apiKeyId] = true;
        delete state.error.delete[apiKeyId];
      })
      .addCase(deleteApiKey.fulfilled, (state, action) => {
        const apiKeyId = action.payload;
        delete state.loading.delete[apiKeyId];
        // 从列表中移除
        state.items = state.items.filter(item => item.id !== action.payload);
        state.total -= 1;
        // 清除当前项（如果是被删除的项）
        if (state.currentItem?.id === action.payload) {
          state.currentItem = null;
        }
      })
      .addCase(deleteApiKey.rejected, (state, action) => {
        const apiKeyId = action.meta.arg;
        delete state.loading.delete[apiKeyId];
        state.error.delete[apiKeyId] = action.payload as string;
      });

    // 测试 API Key
    builder
      .addCase(testApiKey.pending, (state, action) => {
        const id = action.meta.arg;
        state.loading.test[id] = true;
        state.error.test[id] = null;
      })
      .addCase(testApiKey.fulfilled, (state, action) => {
        const { id, success, message, response_time_ms, tested_at } = action.payload;
        state.loading.test[id] = false;
        
        // 更新对应的 API Key 测试结果
        const apiKey = state.items.find(item => item.id === id);
        if (apiKey) {
          apiKey.last_tested_at = tested_at;
          apiKey.test_status = success ? 'success' : 'failed';
          apiKey.test_message = message;
          apiKey.test_response_time = response_time_ms;
        }
      })
      .addCase(testApiKey.rejected, (state, action) => {
        const payload = action.payload as { id: string; message: string };
        state.loading.test[payload.id] = false;
        state.error.test[payload.id] = payload.message;
      });

    // 获取统计信息
    builder
      .addCase(fetchApiKeyStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      });
  },
});

// 导出 actions
export const { 
  clearError, 
  clearAllErrors, 
  resetState, 
  setCurrentItem 
} = apiKeysSlice.actions;

// 导出 reducer
export default apiKeysSlice.reducer;
