import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Settings2, Database, Key } from "lucide-react";

export default function ConfigPage() {
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">配置中心</h1>
        <p className="text-muted-foreground">
          管理 Milvus 连接配置和第三方服务密钥
        </p>
      </div>

      {/* 配置模块卡片 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Milvus 连接配置 */}
        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-primary/10 p-3 rounded-lg">
              <Database className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold">Milvus 连接</h3>
              <p className="text-sm text-muted-foreground">
                配置和管理 Milvus 数据库连接
              </p>
            </div>
          </div>
          <div className="mt-4">
            <Button asChild className="w-full">
              <Link to="/config/milvus">
                管理连接
              </Link>
            </Button>
          </div>
        </Card>

        {/* API 密钥管理 */}
        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-secondary/10 p-3 rounded-lg">
              <Key className="h-6 w-6 text-secondary-foreground" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold">API 密钥</h3>
              <p className="text-sm text-muted-foreground">
                管理第三方服务 API 密钥（向量模型等）
              </p>
            </div>
          </div>
          <div className="mt-4">
            <Button asChild variant="outline" className="w-full">
              <Link to="/config/api-keys">
                管理密钥
              </Link>
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
