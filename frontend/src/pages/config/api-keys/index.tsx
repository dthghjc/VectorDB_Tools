import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Key, ArrowLeft, RefreshCw, CheckCircle, Loader2, AlertCircle, Power, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { useAppDispatch, useAppSelector } from "@/hooks/redux";
import { fetchApiKeys, deleteApiKey, updateApiKey, testApiKey } from "@/store/slices/apiKeysSlice";
import type { ApiKey } from "@/types/apiKeys";

import AddApiKeyDialog from "@/components/features/config/AddApiKeyDialog";

export default function ApiKeysPage() {
  const dispatch = useAppDispatch();
  
  // Redux 状态
  const { items: apiKeys, loading, error, total } = useAppSelector((state) => state.apiKeys);
  
  // 页面加载时获取数据
  useEffect(() => {
    dispatch(fetchApiKeys({}));
  }, [dispatch]);

  // 添加密钥成功后的回调
  const handleAddSuccess = () => {
    // API Key 创建成功后，Redux 会自动更新列表，这里可以显示成功消息
    console.log("API Key 添加成功");
  };

  // 删除 API Key
  const handleDelete = async (apiKey: ApiKey) => {
    if (window.confirm(`确定要删除 "${apiKey.name}" 吗？此操作不可撤销。`)) {
      dispatch(deleteApiKey(apiKey.id));
    }
  };

  // 切换状态
  const handleToggleStatus = async (apiKey: ApiKey) => {
    const newStatus = apiKey.status === 'active' ? 'inactive' : 'active';
    dispatch(updateApiKey({
      id: apiKey.id,
      data: { status: newStatus }
    }));
  };

  // 刷新列表
  const handleRefresh = () => {
    dispatch(fetchApiKeys({}));
  };

  // 测试 API Key
  const handleTest = async (apiKey: ApiKey) => {
    try {
      const result = await dispatch(testApiKey(apiKey.id)).unwrap();
      
      if (result.success) {
        toast.success("API Key 测试成功", {
          description: `响应时间: ${result.response_time_ms?.toFixed(0)}ms`,
          duration: 4000,
        });
      } else {
        toast.error("API Key 测试失败", {
          description: result.message,
          duration: 6000,
          action: {
            label: "重试",
            onClick: () => handleTest(apiKey)
          }
        });
      }
    } catch (error: any) {
      toast.error("测试过程中发生错误", {
        description: error.message || "未知错误",
        duration: 6000,
        action: {
          label: "重试",
          onClick: () => handleTest(apiKey)
        }
      });
    }
  };

  return (
    <div className="space-y-6">


      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">API 密钥管理</h1>
          <p className="text-muted-foreground">
            安全存储和管理第三方服务 API 密钥
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" asChild>
            <Link to="/config">
              <ArrowLeft className="w-4 h-4 mr-2" />
              返回
            </Link>
          </Button>

          <Button variant="outline" onClick={handleRefresh} disabled={loading.list}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading.list ? 'animate-spin' : ''}`} />
            刷新
          </Button>

          {/* 添加密钥按钮 */}
          <AddApiKeyDialog onSuccess={handleAddSuccess} />

        </div>
      </div>

      {/* 错误提示 */}
      {error.list && (
        <Card className="p-4 border-red-200 bg-red-50">
          <p className="text-red-600 text-sm">
            加载失败：{error.list}
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleRefresh}
            className="mt-2"
          >
            重试
          </Button>
        </Card>
      )}

      {/* 密钥列表 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">已保存的密钥</h2>
          <span className="text-sm text-muted-foreground">
            共 {total} 个密钥
          </span>
        </div>

        {loading.list && apiKeys.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">加载中...</p>
          </Card>
        ) : apiKeys.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">暂无 API 密钥</p>
            <p className="text-sm text-muted-foreground mt-1">
              点击上方"添加密钥"按钮开始添加
            </p>
          </Card>
        ) : (
          apiKeys.map((key) => (
          <Card key={key.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-orange-100 p-3 rounded-lg">
                  <Key className="h-6 w-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground">{key.name}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    提供商：<span className="font-medium text-foreground">{key.provider}</span>
                  </p>
                  <div className="mt-2">
                    <span className="text-xs text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                      {key.key_preview}
                    </span>
                  </div>
                  <div className="mt-2 space-y-1">
                    <p className="text-xs text-muted-foreground">
                      <span className="text-muted-foreground/70">Base URL：</span>
                      <span className="font-medium text-blue-600 break-all">{key.base_url}</span>
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-muted-foreground/70">最后使用：</span>
                      <span className="font-medium">{key.last_used_at || '从未使用'}</span>
                      <span className="mx-2">•</span>
                      <span className="text-muted-foreground/70">创建于：</span>
                      <span className="font-medium">{new Date(key.created_at).toLocaleString()}</span>
                    </p>
                    {/* 测试状态 */}
                    <p className="text-xs text-muted-foreground">
                      <span className="text-muted-foreground/70">最后测试：</span>
                      <span className="font-medium">
                        {key.last_tested_at 
                          ? new Date(key.last_tested_at).toLocaleString()
                          : '从未测试'
                        }
                      </span>
                      {key.test_status && (
                        <>
                          <span className="mx-2">•</span>
                          <span className={`font-medium inline-flex items-center gap-1 ${
                            key.test_status === 'success' ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {key.test_status === 'success' ? (
                              <>
                                <CheckCircle className="w-3 h-3" />
                                正常
                              </>
                            ) : (
                              <>
                                <AlertCircle className="w-3 h-3" />
                                异常
                              </>
                            )}
                          </span>
                        </>
                      )}
                    </p>

                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                    key.status === "active" 
                      ? "bg-green-100 text-green-800" 
                      : "bg-gray-100 text-gray-800"
                  }`}>
                    {key.status === "active" ? "活跃" : "未使用"}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleToggleStatus(key)}
                    disabled={loading.update[key.id]}
                  >
                    <Power className="w-3 h-3 mr-1" />
                    {key.status === 'active' ? '禁用' : '启用'}
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleTest(key)}
                    disabled={loading.test[key.id]}
                  >
                    {loading.test[key.id] ? (
                      <>
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                        测试中
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-3 h-3 mr-1" />
                        测试
                      </>
                    )}
                  </Button>

                  <Button 
                    variant="destructive" 
                    size="sm"
                    onClick={() => handleDelete(key)}
                    disabled={loading.delete}
                  >
                    <Trash2 className="w-3 h-3 mr-1" />
                    删除
                  </Button>
                </div>
              </div>
            </div>
          </Card>
          ))
        )}
      </div>
    </div>
  );
}
