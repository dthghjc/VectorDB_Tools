import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { milvusConnectionService } from '@/services/api/milvusConnections';
import type { 
  MilvusConnection, 
  CreateMilvusConnectionRequest,
  UpdateMilvusConnectionRequest,
  TestMilvusConnectionRequest
} from '@/types/milvusConnections';

/**
 * Milvus 连接配置状态接口
 */
interface MilvusConnectionsState {
  // 数据状态
  items: MilvusConnection[];
  currentItem: MilvusConnection | null;
  
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
    recently_used: number;
    by_status: Record<string, number>;
    by_secure: Record<string, number>;
  } | null;
}

/**
 * 初始状态
 */
const initialState: MilvusConnectionsState = {
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
 * 异步 Action：创建 Milvus 连接配置
 */
export const createMilvusConnection = createAsyncThunk(
  'milvusConnections/create',
  async (data: CreateMilvusConnectionRequest, { rejectWithValue }) => {
    try {
      const response = await milvusConnectionService.create(data);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '创建失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：获取 Milvus 连接配置列表
 */
export const fetchMilvusConnections = createAsyncThunk(
  'milvusConnections/fetchList',
  async ({ 
    page = 1, 
    size = 10,
    status
  }: { 
    page?: number; 
    size?: number;
    status?: 'active' | 'inactive';
  } = {}, { rejectWithValue }) => {
    try {
      const response = await milvusConnectionService.getList(page, size, status);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '获取列表失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：获取单个 Milvus 连接配置
 */
export const fetchMilvusConnectionById = createAsyncThunk(
  'milvusConnections/fetchById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await milvusConnectionService.getById(id);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '获取详情失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：更新 Milvus 连接配置
 */
export const updateMilvusConnection = createAsyncThunk(
  'milvusConnections/update',
  async ({ id, data }: { id: string; data: UpdateMilvusConnectionRequest }, { rejectWithValue }) => {
    try {
      const response = await milvusConnectionService.update(id, data);
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '更新失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 异步 Action：删除 Milvus 连接配置
 */
export const deleteMilvusConnection = createAsyncThunk(
  'milvusConnections/delete',
  async (id: string, { rejectWithValue }) => {
    try {
      await milvusConnectionService.delete(id);
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
export const fetchMilvusConnectionStats = createAsyncThunk(
  'milvusConnections/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await milvusConnectionService.getStats();
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || '获取统计失败';
      return rejectWithValue(message);
    }
  }
);

/**
 * 测试 Milvus 连接配置
 */
export const testMilvusConnection = createAsyncThunk(
  'milvusConnections/test',
  async ({ id, options }: { id: string; options?: TestMilvusConnectionRequest }, { rejectWithValue }) => {
    try {
      const response = await milvusConnectionService.test(id, options);
      return { id, ...response };
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Milvus 连接测试失败';
      return rejectWithValue({ id, message });
    }
  }
);

/**
 * Milvus 连接配置 Slice
 */
const milvusConnectionsSlice = createSlice({
  name: 'milvusConnections',
  initialState,
  reducers: {
    // 清除特定错误
    clearError: (state, action: PayloadAction<keyof MilvusConnectionsState['error']>) => {
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
    setCurrentItem: (state, action: PayloadAction<MilvusConnection | null>) => {
      state.currentItem = action.payload;
    },
  },
  extraReducers: (builder) => {
    // 创建 Milvus 连接配置
    builder
      .addCase(createMilvusConnection.pending, (state) => {
        state.loading.create = true;
        state.error.create = null;
      })
      .addCase(createMilvusConnection.fulfilled, (state, action) => {
        state.loading.create = false;
        // 将新创建的项添加到列表开头
        const newItem: MilvusConnection = {
          ...action.payload,
          user_id: '', // 后端会返回，这里先设为空
          last_used_at: null, // 新创建的连接配置从未使用
          last_tested_at: null,
          test_status: null,
          test_message: null,
          test_response_time: null,
        };
        state.items.unshift(newItem);
        state.total += 1;
      })
      .addCase(createMilvusConnection.rejected, (state, action) => {
        state.loading.create = false;
        state.error.create = action.payload as string;
      });

    // 获取列表
    builder
      .addCase(fetchMilvusConnections.pending, (state) => {
        state.loading.list = true;
        state.error.list = null;
      })
      .addCase(fetchMilvusConnections.fulfilled, (state, action) => {
        state.loading.list = false;
        state.items = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.size = action.payload.size;
      })
      .addCase(fetchMilvusConnections.rejected, (state, action) => {
        state.loading.list = false;
        state.error.list = action.payload as string;
      });

    // 获取单个详情
    builder
      .addCase(fetchMilvusConnectionById.fulfilled, (state, action) => {
        state.currentItem = action.payload;
      });

    // 更新 Milvus 连接配置
    builder
      .addCase(updateMilvusConnection.pending, (state, action) => {
        const connectionId = action.meta.arg.id;
        state.loading.update[connectionId] = true;
        delete state.error.update[connectionId];
      })
      .addCase(updateMilvusConnection.fulfilled, (state, action) => {
        const connectionId = action.payload.id;
        delete state.loading.update[connectionId];
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
      .addCase(updateMilvusConnection.rejected, (state, action) => {
        const connectionId = action.meta.arg.id;
        delete state.loading.update[connectionId];
        state.error.update[connectionId] = action.payload as string;
      });

    // 删除 Milvus 连接配置
    builder
      .addCase(deleteMilvusConnection.pending, (state, action) => {
        const connectionId = action.meta.arg;
        state.loading.delete[connectionId] = true;
        delete state.error.delete[connectionId];
      })
      .addCase(deleteMilvusConnection.fulfilled, (state, action) => {
        const connectionId = action.payload;
        delete state.loading.delete[connectionId];
        // 从列表中移除
        state.items = state.items.filter(item => item.id !== action.payload);
        state.total -= 1;
        // 清除当前项（如果是被删除的项）
        if (state.currentItem?.id === action.payload) {
          state.currentItem = null;
        }
      })
      .addCase(deleteMilvusConnection.rejected, (state, action) => {
        const connectionId = action.meta.arg;
        delete state.loading.delete[connectionId];
        state.error.delete[connectionId] = action.payload as string;
      });

    // 测试 Milvus 连接配置
    builder
      .addCase(testMilvusConnection.pending, (state, action) => {
        const id = action.meta.arg.id;
        state.loading.test[id] = true;
        state.error.test[id] = null;
      })
      .addCase(testMilvusConnection.fulfilled, (state, action) => {
        const { id, success, message, response_time_ms, tested_at, server_version, collections_count } = action.payload;
        state.loading.test[id] = false;
        
        // 更新对应的 Milvus 连接配置测试结果
        const connection = state.items.find(item => item.id === id);
        if (connection) {
          connection.last_tested_at = tested_at;
          connection.test_status = success ? 'success' : 'failed';
          connection.test_message = message;
          connection.test_response_time = response_time_ms;
          
          // 如果测试成功且有额外信息，更新消息
          if (success && (server_version || collections_count !== undefined)) {
            const extraInfo = [];
            if (server_version) extraInfo.push(`版本: ${server_version}`);
            if (collections_count !== undefined) extraInfo.push(`集合数: ${collections_count}`);
            
            if (extraInfo.length > 0) {
              connection.test_message += ` (${extraInfo.join(', ')})`;
            }
          }
        }
      })
      .addCase(testMilvusConnection.rejected, (state, action) => {
        const payload = action.payload as { id: string; message: string };
        state.loading.test[payload.id] = false;
        state.error.test[payload.id] = payload.message;
      });

    // 获取统计信息
    builder
      .addCase(fetchMilvusConnectionStats.fulfilled, (state, action) => {
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
} = milvusConnectionsSlice.actions;

// 导出 reducer
export default milvusConnectionsSlice.reducer;
