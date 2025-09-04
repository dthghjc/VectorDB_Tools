import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { apiKeyService } from '@/services/api/apiKeys';
import type { 
  ApiKey, 
  CreateApiKeyRequest, 
  CreateApiKeyResponse 
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
    update: boolean;
    delete: boolean;
    test: boolean;
  };
  
  // 错误状态
  error: {
    list: string | null;
    create: string | null;
    update: string | null;
    delete: string | null;
    test: string | null;
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
    update: false,
    delete: false,
    test: false,
  },
  error: {
    list: null,
    create: null,
    update: null,
    delete: null,
    test: null,
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
 * API Keys Slice
 */
const apiKeysSlice = createSlice({
  name: 'apiKeys',
  initialState,
  reducers: {
    // 清除特定错误
    clearError: (state, action: PayloadAction<keyof ApiKeysState['error']>) => {
      state.error[action.payload] = null;
    },
    
    // 清除所有错误
    clearAllErrors: (state) => {
      Object.keys(state.error).forEach((key) => {
        state.error[key as keyof typeof state.error] = null;
      });
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
          key_preview: action.payload.key_preview || '', // 确保有预览
          last_used_at: null,
          updated_at: action.payload.created_at
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
      .addCase(updateApiKey.pending, (state) => {
        state.loading.update = true;
        state.error.update = null;
      })
      .addCase(updateApiKey.fulfilled, (state, action) => {
        state.loading.update = false;
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
        state.loading.update = false;
        state.error.update = action.payload as string;
      });

    // 删除 API Key
    builder
      .addCase(deleteApiKey.pending, (state) => {
        state.loading.delete = true;
        state.error.delete = null;
      })
      .addCase(deleteApiKey.fulfilled, (state, action) => {
        state.loading.delete = false;
        // 从列表中移除
        state.items = state.items.filter(item => item.id !== action.payload);
        state.total -= 1;
        // 清除当前项（如果是被删除的项）
        if (state.currentItem?.id === action.payload) {
          state.currentItem = null;
        }
      })
      .addCase(deleteApiKey.rejected, (state, action) => {
        state.loading.delete = false;
        state.error.delete = action.payload as string;
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
