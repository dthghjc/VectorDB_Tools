import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Upload, Bot, Database, CheckCircle, ArrowRight } from "lucide-react";

// 导入步骤定义
const importSteps = [
  {
    id: "upload",
    title: "上传数据",
    description: "上传您的原始数据文件",
    icon: Upload,
    path: "/data-import/upload",
    status: "pending" as const
  },
  {
    id: "vectorize", 
    title: "向量化",
    description: "选择模型并配置字段映射",
    icon: Bot,
    path: "/data-import/vectorize",
    status: "pending" as const
  },
  {
    id: "load",
    title: "加载数据",
    description: "将向量化数据导入 Milvus",
    icon: Database,
    path: "/data-import/load", 
    status: "pending" as const
  }
];

// 最近的导入任务（模拟数据）
const recentImports = [
  {
    id: "1",
    name: "产品文档向量化",
    fileName: "products.csv",
    status: "completed",
    progress: 100,
    recordsCount: 1500,
    createdAt: "2024-01-15 14:30:00"
  },
  {
    id: "2",
    name: "用户评论数据",
    fileName: "reviews.json", 
    status: "processing",
    progress: 65,
    recordsCount: 3200,
    createdAt: "2024-01-15 16:20:00"
  },
  {
    id: "3",
    name: "FAQ知识库",
    fileName: "faq.txt",
    status: "failed",
    progress: 0,
    recordsCount: 0,
    createdAt: "2024-01-15 12:10:00"
  }
];

export default function DataImportPage() {
  const [currentStep] = useState(0);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-100";
      case "processing":
        return "text-blue-600 bg-blue-100";
      case "failed":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "已完成";
      case "processing":
        return "处理中";
      case "failed":
        return "失败";
      default:
        return "等待中";
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">数据导入流水线</h1>
        <p className="text-muted-foreground">
          引导式的数据处理流程：上传 → 向量化 → 加载到 Milvus
        </p>
      </div>

      {/* 流程步骤 */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-6">导入流程</h2>
        <div className="relative">
          {/* 步骤连接线 */}
          <div className="absolute top-12 left-12 right-12 h-0.5 bg-gray-200 -z-10"></div>
          
          <div className="flex justify-between">
            {importSteps.map((step, index) => {
              const Icon = step.icon;
              const isCompleted = index < currentStep;
              const isCurrent = index === currentStep;
              
              return (
                <div key={step.id} className="flex flex-col items-center space-y-3 relative">
                  {/* 步骤圆圈 */}
                  <div className={`
                    w-24 h-24 rounded-full flex items-center justify-center
                    ${isCompleted 
                      ? "bg-green-100 text-green-600" 
                      : isCurrent 
                        ? "bg-blue-100 text-blue-600" 
                        : "bg-gray-100 text-gray-400"
                    }
                  `}>
                    {isCompleted ? (
                      <CheckCircle className="w-8 h-8" />
                    ) : (
                      <Icon className="w-8 h-8" />
                    )}
                  </div>
                  
                  {/* 步骤信息 */}
                  <div className="text-center max-w-32">
                    <h3 className="font-semibold text-sm">{step.title}</h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      {step.description}
                    </p>
                  </div>
                  
                  {/* 开始按钮 */}
                  <Button asChild size="sm" variant={isCurrent ? "default" : "outline"}>
                    <Link to={step.path}>
                      {isCompleted ? "重新执行" : isCurrent ? "开始" : "等待"}
                    </Link>
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      </Card>

      {/* 快速开始 */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Upload className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold">新建导入任务</h3>
              <p className="text-sm text-muted-foreground">
                从头开始一个新的数据导入流程
              </p>
            </div>
          </div>
          <Button asChild className="w-full mt-4">
            <Link to="/data-import/upload">
              <Upload className="w-4 h-4 mr-2" />
              开始导入
            </Link>
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <Bot className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold">批量向量化</h3>
              <p className="text-sm text-muted-foreground">
                对已上传的文件进行批量向量化
              </p>
            </div>
          </div>
          <Button asChild variant="outline" className="w-full mt-4">
            <Link to="/data-import/vectorize">
              <Bot className="w-4 h-4 mr-2" />
              向量化
            </Link>
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Database className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold">数据加载</h3>
              <p className="text-sm text-muted-foreground">
                将向量数据导入到 Milvus Collection
              </p>
            </div>
          </div>
          <Button asChild variant="outline" className="w-full mt-4">
            <Link to="/data-import/load">
              <Database className="w-4 h-4 mr-2" />
              加载数据
            </Link>
          </Button>
        </Card>
      </div>

      {/* 最近的导入任务 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">最近的导入任务</h2>
          <Button variant="outline" asChild>
            <Link to="/tasks">
              查看所有任务
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>

        <div className="space-y-3">
          {recentImports.map((task) => (
            <Card key={task.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-slate-100 p-2 rounded-lg">
                    <Upload className="h-5 w-5 text-slate-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{task.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      文件：{task.fileName} • {task.recordsCount > 0 ? `${task.recordsCount} 条记录` : ""}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      创建时间：{task.createdAt}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  {/* 进度条 */}
                  {task.status === "processing" && (
                    <div className="w-24">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${task.progress}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-center mt-1">{task.progress}%</p>
                    </div>
                  )}
                  
                  {/* 状态标签 */}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                    {getStatusText(task.status)}
                  </span>
                  
                  <Button variant="outline" size="sm">
                    查看详情
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* 使用提示 */}
      <Card className="p-6 bg-amber-50 border-amber-200">
        <div className="flex items-start space-x-3">
          <Upload className="h-5 w-5 text-amber-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-amber-900">导入指南</h3>
            <div className="text-sm text-amber-700 mt-1 space-y-1">
              <p>• <strong>支持格式：</strong>CSV、JSON、TXT、Excel 文件</p>
              <p>• <strong>向量化：</strong>支持 OpenAI、Google PaLM 等多种模型</p>
              <p>• <strong>批量处理：</strong>大文件会自动分批处理，可实时查看进度</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
