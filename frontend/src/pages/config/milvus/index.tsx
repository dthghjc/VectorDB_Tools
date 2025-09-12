import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Database, ArrowLeft, RefreshCw, CheckCircle, Loader2, AlertCircle, Power, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { useAppDispatch, useAppSelector } from "@/hooks/redux";
import { 
  fetchMilvusConnections, 
  deleteMilvusConnection, 
  updateMilvusConnection, 
  testMilvusConnection 
} from "@/store/slices/milvusConnectionsSlice";
import type { MilvusConnection } from "@/types/milvusConnections";

import AddMilvusConnectionDialog from "@/components/features/config/AddMilvusConnectionDialog";

export default function MilvusConfigPage() {
  const dispatch = useAppDispatch();
  
  // Redux 状态
  const { items: connections, loading, error, total } = useAppSelector((state) => state.milvusConnections);
  
  // 删除对话框状态
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [connectionToDelete, setConnectionToDelete] = useState<MilvusConnection | null>(null);
  
  // 页面加载时获取数据
  useEffect(() => {
    dispatch(fetchMilvusConnections({}));
  }, [dispatch]);

  // 添加连接成功后的回调
  const handleAddSuccess = () => {
    // 连接配置创建成功后，Redux 会自动更新列表，这里可以显示成功消息
    console.log("Milvus 连接配置添加成功");
  };

  // 打开删除确认对话框
  const handleDeleteClick = (connection: MilvusConnection) => {
    setConnectionToDelete(connection);
    setDeleteDialogOpen(true);
  };

  // 确认删除连接配置
  const handleDeleteConfirm = async () => {
    if (connectionToDelete) {
      dispatch(deleteMilvusConnection(connectionToDelete.id));
      setDeleteDialogOpen(false);
      setConnectionToDelete(null);
    }
  };

  // 取消删除
  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setConnectionToDelete(null);
  };

  // 切换状态
  const handleToggleStatus = async (connection: MilvusConnection) => {
    const newStatus = connection.status === 'active' ? 'inactive' : 'active';
    dispatch(updateMilvusConnection({
      id: connection.id,
      data: { status: newStatus }
    }));
  };

  // 刷新列表
  const handleRefresh = () => {
    dispatch(fetchMilvusConnections({}));
  };

  // 测试连接配置
  const handleTest = async (connection: MilvusConnection) => {
    try {
      const result = await dispatch(testMilvusConnection({ 
        id: connection.id,
        options: { timeout_seconds: 10 }
      })).unwrap();
      
      if (result.success) {
        const description = [];
        if (result.response_time_ms) {
          description.push(`响应时间: ${result.response_time_ms.toFixed(0)}ms`);
        }
        if (result.server_version) {
          description.push(`服务器版本: ${result.server_version}`);
        }
        if (result.collections_count !== undefined) {
          description.push(`集合数量: ${result.collections_count}`);
        }

        toast.success("Milvus 连接测试成功", {
          description: description.join(' | '),
          duration: 4000,
        });
      } else {
        toast.error("Milvus 连接测试失败", {
          description: result.message,
          duration: 6000,
          action: {
            label: "重试",
            onClick: () => handleTest(connection)
          }
        });
      }
    } catch (error: any) {
      toast.error("测试过程中发生错误", {
        description: error.message || "未知错误",
        duration: 6000,
        action: {
          label: "重试",
          onClick: () => handleTest(connection)
        }
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Milvus 连接管理</h1>
          <p className="text-muted-foreground">
            配置和测试 Milvus 数据库连接
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

          {/* 添加连接按钮 */}
          <AddMilvusConnectionDialog onSuccess={handleAddSuccess} />
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

      {/* 连接配置列表 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">已配置的连接</h2>
          <span className="text-sm text-muted-foreground">
            共 {total} 个连接配置
          </span>
        </div>

        {loading.list && connections.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">加载中...</p>
          </Card>
        ) : connections.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">暂无 Milvus 连接配置</p>
            <p className="text-sm text-muted-foreground mt-1">
              点击上方"添加连接"按钮开始配置
            </p>
          </Card>
        ) : (
          connections.map((connection) => (
          <Card key={connection.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Database className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground">{connection.name}</h3>
                  
                  {/* 连接信息 */}
                  <div className="mt-2 space-y-1">
                    <p className="text-sm text-muted-foreground">
                      <span className="text-muted-foreground/70">主机:</span>
                      <span className="font-medium text-foreground ml-1">{connection.host}:{connection.port}</span>
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <span className="text-muted-foreground/70">数据库:</span>
                      <span className="font-medium text-foreground ml-1">{connection.database_name}</span>
                    </p>
                    {connection.username && (
                      <p className="text-sm text-muted-foreground">
                        <span className="text-muted-foreground/70">用户:</span>
                        <span className="font-medium text-foreground ml-1 font-mono bg-muted px-2 py-0.5 rounded text-xs">
                          {connection.username}
                        </span>
                      </p>
                    )}
                  </div>

                  {/* 描述信息 */}
                  {connection.description && (
                    <p className="text-sm text-muted-foreground mt-2 italic">
                      {connection.description}
                    </p>
                  )}
                  <div className="mt-2 space-y-1">
                    <p className="text-xs text-muted-foreground">
                      <span className="text-muted-foreground/70">最后使用：</span>
                      <span className="font-medium">{connection.last_used_at || '从未使用'}</span>
                      <span className="mx-2">•</span>
                      <span className="text-muted-foreground/70">创建于：</span>
                      <span className="font-medium">{new Date(connection.created_at).toLocaleString()}</span>
                    </p>
                    {/* 测试状态 */}
                    <p className="text-xs text-muted-foreground">
                      <span className="text-muted-foreground/70">最后测试：</span>
                      <span className="font-medium">
                        {connection.last_tested_at 
                          ? new Date(connection.last_tested_at).toLocaleString()
                          : '从未测试'
                        }
                      </span>
                      {connection.test_status && (
                        <>
                          <span className="mx-2">•</span>
                          <span className={`font-medium inline-flex items-center gap-1 ${
                            connection.test_status === 'success' ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {connection.test_status === 'success' ? (
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
                    connection.status === "active" 
                      ? "bg-green-100 text-green-800" 
                      : "bg-gray-100 text-gray-800"
                  }`}>
                    {connection.status === "active" ? "活跃" : "禁用"}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleToggleStatus(connection)}
                    disabled={loading.update[connection.id]}
                  >
                    <Power className="w-3 h-3 mr-1" />
                    {connection.status === 'active' ? '禁用' : '启用'}
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleTest(connection)}
                    disabled={loading.test[connection.id]}
                  >
                    {loading.test[connection.id] ? (
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
                    onClick={() => handleDeleteClick(connection)}
                    disabled={loading.delete[connection.id]}
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

      {/* 删除确认对话框 */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>删除 Milvus 连接配置</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除 "{connectionToDelete?.name}" 连接配置吗？
              <br />
              <span className="text-red-600 font-medium">此操作不可撤销。</span>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleDeleteCancel}>
              取消
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteConfirm}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              确认删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
