import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Database, CheckCircle, XCircle, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

// 模拟的 Milvus 连接数据
const mockConnections = [
  {
    id: "1",
    name: "生产环境",
    host: "milvus-prod.example.com",
    port: 19530,
    status: "connected",
    lastTest: "2024-01-15 10:30:00"
  },
  {
    id: "2", 
    name: "测试环境",
    host: "milvus-test.example.com", 
    port: 19530,
    status: "disconnected",
    lastTest: "2024-01-15 09:15:00"
  }
];

export default function MilvusConfigPage() {
  const [connections] = useState(mockConnections);
  const [showAddForm, setShowAddForm] = useState(false);

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
          <Button onClick={() => setShowAddForm(!showAddForm)}>
            <Plus className="w-4 h-4 mr-2" />
            添加连接
          </Button>
        </div>
      </div>

      {/* 添加连接表单 */}
      {showAddForm && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">添加新连接</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">连接名称</Label>
              <Input id="name" placeholder="例如：生产环境" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="host">主机地址</Label>
              <Input id="host" placeholder="例如：localhost" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="port">端口</Label>
              <Input id="port" type="number" placeholder="19530" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="database">数据库</Label>
              <Input id="database" placeholder="default" />
            </div>
          </div>
          <div className="flex justify-end space-x-2 mt-4">
            <Button variant="outline" onClick={() => setShowAddForm(false)}>
              取消
            </Button>
            <Button>
              测试连接
            </Button>
            <Button variant="default">
              保存
            </Button>
          </div>
        </Card>
      )}

      {/* 连接列表 */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">现有连接</h2>
        {connections.map((conn) => (
          <Card key={conn.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Database className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{conn.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {conn.host}:{conn.port}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    最后测试：{conn.lastTest}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {conn.status === "connected" ? (
                    <>
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span className="text-sm text-green-600">已连接</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-5 w-5 text-red-500" />
                      <span className="text-sm text-red-600">未连接</span>
                    </>
                  )}
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    测试
                  </Button>
                  <Button variant="outline" size="sm">
                    编辑
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
