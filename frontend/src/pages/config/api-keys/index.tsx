import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Key, Eye, EyeOff, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";

// 模拟的 API 密钥数据
const mockApiKeys = [
  {
    id: "1",
    name: "OpenAI GPT-4",
    provider: "OpenAI",
    keyPreview: "sk-proj-****...****abcd",
    status: "active",
    lastUsed: "2024-01-15 14:30:00",
    createdAt: "2024-01-10 09:00:00"
  },
  {
    id: "2",
    name: "Google PaLM",
    provider: "Google",
    keyPreview: "AIza****...****xyz9",
    status: "inactive",
    lastUsed: "从未使用",
    createdAt: "2024-01-12 16:45:00"
  }
];

export default function ApiKeysPage() {
  const [apiKeys] = useState(mockApiKeys);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showKey, setShowKey] = useState<string | null>(null);

  const toggleKeyVisibility = (keyId: string) => {
    setShowKey(showKey === keyId ? null : keyId);
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
          <Button onClick={() => setShowAddForm(!showAddForm)}>
            <Plus className="w-4 h-4 mr-2" />
            添加密钥
          </Button>
        </div>
      </div>

      {/* 添加密钥表单 */}
      {showAddForm && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">添加新 API 密钥</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="keyName">密钥名称</Label>
              <Input id="keyName" placeholder="例如：OpenAI GPT-4" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="provider">服务提供商</Label>
              <Input id="provider" placeholder="例如：OpenAI" />
            </div>
            <div className="md:col-span-2 space-y-2">
              <Label htmlFor="apiKey">API 密钥</Label>
              <Input 
                id="apiKey" 
                type="password" 
                placeholder="粘贴您的 API 密钥"
              />
              <p className="text-xs text-muted-foreground">
                密钥将被安全加密存储，仅显示前后几位字符
              </p>
            </div>
          </div>
          <div className="flex justify-end space-x-2 mt-4">
            <Button variant="outline" onClick={() => setShowAddForm(false)}>
              取消
            </Button>
            <Button variant="default">
              保存密钥
            </Button>
          </div>
        </Card>
      )}

      {/* 密钥列表 */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">已保存的密钥</h2>
        {apiKeys.map((key) => (
          <Card key={key.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-orange-100 p-3 rounded-lg">
                  <Key className="h-6 w-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{key.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    提供商：{key.provider}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-muted-foreground font-mono">
                      {showKey === key.id ? "sk-proj-1234567890abcdef1234567890abcdef" : key.keyPreview}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleKeyVisibility(key.id)}
                    >
                      {showKey === key.id ? (
                        <EyeOff className="h-3 w-3" />
                      ) : (
                        <Eye className="h-3 w-3" />
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    最后使用：{key.lastUsed} • 创建于：{key.createdAt}
                  </p>
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
                  <Button variant="outline" size="sm">
                    测试
                  </Button>
                  <Button variant="outline" size="sm">
                    编辑
                  </Button>
                  <Button variant="destructive" size="sm">
                    删除
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* 安全提示 */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="flex items-start space-x-3">
          <Key className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-blue-900">安全提示</h3>
            <p className="text-sm text-blue-700 mt-1">
              • 所有 API 密钥都经过加密存储<br/>
              • 定期轮换您的 API 密钥以确保安全<br/>
              • 不要在公共环境中显示完整密钥
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
