import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Database, Key, ArrowRight } from "lucide-react";

export default function ConfigPage() {
  return (
    <div className="space-y-8">
      {/* 页面标题 */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">配置中心</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          统一管理 Milvus 连接配置和第三方服务密钥，为你的向量数据库工作流提供基础设施支持
        </p>
      </div>

      {/* 配置模块网格 */}
      <div className="grid gap-8 md:grid-cols-2 lg:gap-12">
        {/* Milvus 连接配置 - 主要功能 */}
        <Card className="group relative overflow-hidden border-2 border-primary/20 hover:border-primary/40 transition-all duration-300 hover:shadow-lg">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
          <div className="relative p-8">
            <div className="flex items-start space-x-6">
              <div className="bg-primary p-4 rounded-xl shadow-md">
                <Database className="h-8 w-8 text-primary-foreground" />
              </div>
              <div className="flex-1 space-y-3">
                <div>
                  <h3 className="text-xl font-bold text-primary">Milvus 连接</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    核心数据库配置
                  </p>
                </div>
                <p className="text-muted-foreground leading-relaxed">
                  配置和管理 Milvus 向量数据库连接，建立数据存储的基础链路
                </p>
              </div>
            </div>
            <div className="mt-8">
              <Button asChild size="lg" className="w-full group">
                <Link to="/config/milvus" className="flex items-center justify-center space-x-2">
                  <span>管理连接</span>
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
            </div>
          </div>
        </Card>

        {/* API 密钥管理 - 辅助功能 */}
        <Card className="group relative overflow-hidden hover:shadow-md transition-all duration-300 border-muted-foreground/20">
          <div className="p-8">
            <div className="flex items-start space-x-6">
              <div className="bg-muted p-4 rounded-xl">
                <Key className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="flex-1 space-y-3">
                <div>
                  <h3 className="text-xl font-semibold">API 密钥</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    第三方服务集成
                  </p>
                </div>
                <p className="text-muted-foreground leading-relaxed">
                  安全管理向量模型 API 密钥，支持多种向量化服务的接入
                </p>
              </div>
            </div>
            <div className="mt-8">
              <Button asChild variant="outline" size="lg" className="w-full group">
                <Link to="/config/api-keys" className="flex items-center justify-center space-x-2">
                  <span>管理密钥</span>
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
