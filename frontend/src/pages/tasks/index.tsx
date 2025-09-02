import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Clock,
  Filter,
  MoreHorizontal
} from "lucide-react";

// 任务状态类型
type TaskStatus = "pending" | "running" | "completed" | "failed" | "paused";

// 任务类型
interface Task {
  id: string;
  name: string;
  type: "vectorization" | "data_loading" | "batch_search";
  status: TaskStatus;
  progress: number;
  startTime: string;
  endTime?: string;
  duration?: string;
  details: {
    totalRecords?: number;
    processedRecords?: number;
    errorCount?: number;
    model?: string;
    collection?: string;
  };
}

// 模拟任务数据
const mockTasks: Task[] = [
  {
    id: "1",
    name: "产品文档向量化",
    type: "vectorization",
    status: "running",
    progress: 75,
    startTime: "2024-01-15 14:30:00",
    details: {
      totalRecords: 1500,
      processedRecords: 1125,
      errorCount: 0,
      model: "text-embedding-ada-002"
    }
  },
  {
    id: "2", 
    name: "用户评论数据导入",
    type: "data_loading",
    status: "completed",
    progress: 100,
    startTime: "2024-01-15 13:20:00",
    endTime: "2024-01-15 13:45:00",
    duration: "25分钟",
    details: {
      totalRecords: 3200,
      processedRecords: 3200,
      errorCount: 0,
      collection: "user_reviews"
    }
  },
  {
    id: "3",
    name: "FAQ 知识库向量化", 
    type: "vectorization",
    status: "failed",
    progress: 35,
    startTime: "2024-01-15 12:10:00",
    endTime: "2024-01-15 12:25:00",
    duration: "15分钟",
    details: {
      totalRecords: 800,
      processedRecords: 280,
      errorCount: 45,
      model: "text-embedding-ada-002"
    }
  },
  {
    id: "4",
    name: "批量相似度检索测试",
    type: "batch_search", 
    status: "pending",
    progress: 0,
    startTime: "2024-01-15 16:00:00",
    details: {
      totalRecords: 100,
      processedRecords: 0,
      collection: "product_vectors"
    }
  },
  {
    id: "5",
    name: "图片特征向量化",
    type: "vectorization",
    status: "paused",
    progress: 45,
    startTime: "2024-01-15 15:30:00", 
    details: {
      totalRecords: 2000,
      processedRecords: 900,
      errorCount: 12,
      model: "clip-vit-base-patch32"
    }
  }
];

export default function TasksPage() {
  const [tasks] = useState(mockTasks);
  const [filterStatus, setFilterStatus] = useState<TaskStatus | "all">("all");

  // 获取状态样式
  const getStatusStyle = (status: TaskStatus) => {
    switch (status) {
      case "running":
        return "text-blue-600 bg-blue-100";
      case "completed":
        return "text-green-600 bg-green-100";
      case "failed":
        return "text-red-600 bg-red-100";
      case "paused":
        return "text-yellow-600 bg-yellow-100";
      case "pending":
        return "text-gray-600 bg-gray-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  // 获取状态图标
  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case "running":
        return <RefreshCw className="w-4 h-4 animate-spin" />;
      case "completed":
        return <CheckCircle className="w-4 h-4" />;
      case "failed":
        return <XCircle className="w-4 h-4" />;
      case "paused":
        return <Pause className="w-4 h-4" />;
      case "pending":
        return <Clock className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  // 获取状态文本
  const getStatusText = (status: TaskStatus) => {
    switch (status) {
      case "running":
        return "运行中";
      case "completed":
        return "已完成";
      case "failed":
        return "失败";
      case "paused":
        return "已暂停";
      case "pending":
        return "等待中";
      default:
        return "未知";
    }
  };

  // 获取任务类型文本
  const getTaskTypeText = (type: string) => {
    switch (type) {
      case "vectorization":
        return "向量化";
      case "data_loading":
        return "数据导入";
      case "batch_search":
        return "批量检索";
      default:
        return "未知类型";
    }
  };

  // 过滤任务
  const filteredTasks = filterStatus === "all" 
    ? tasks 
    : tasks.filter(task => task.status === filterStatus);

  // 统计数据
  const stats = {
    total: tasks.length,
    running: tasks.filter(t => t.status === "running").length,
    completed: tasks.filter(t => t.status === "completed").length,
    failed: tasks.filter(t => t.status === "failed").length,
    pending: tasks.filter(t => t.status === "pending").length
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">任务中心</h1>
        <p className="text-muted-foreground">
          监控和管理所有后台任务的执行状态
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold">{stats.total}</div>
          <div className="text-sm text-muted-foreground">总任务数</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{stats.running}</div>
          <div className="text-sm text-muted-foreground">运行中</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          <div className="text-sm text-muted-foreground">已完成</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          <div className="text-sm text-muted-foreground">失败</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-gray-600">{stats.pending}</div>
          <div className="text-sm text-muted-foreground">等待中</div>
        </Card>
      </div>

      {/* 过滤和操作栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <select
            className="px-3 py-2 border border-input rounded-md text-sm"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as TaskStatus | "all")}
          >
            <option value="all">所有状态</option>
            <option value="running">运行中</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
            <option value="pending">等待中</option>
            <option value="paused">已暂停</option>
          </select>
        </div>
        <Button>
          <RefreshCw className="w-4 h-4 mr-2" />
          刷新
        </Button>
      </div>

      {/* 任务列表 */}
      <div className="space-y-4">
        {filteredTasks.map((task) => (
          <Card key={task.id} className="p-6">
            <div className="flex items-center justify-between">
              {/* 任务基本信息 */}
              <div className="flex items-center space-x-4 flex-1">
                <div className="bg-slate-100 p-3 rounded-lg">
                  {getStatusIcon(task.status)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{task.name}</h3>
                    <span className="text-sm px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                      {getTaskTypeText(task.type)}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusStyle(task.status)}`}>
                      {getStatusText(task.status)}
                    </span>
                  </div>
                  
                  {/* 进度条 */}
                  {task.status !== "pending" && (
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>进度</span>
                        <span>{task.progress}%</span>
                      </div>
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${
                            task.status === "failed" ? "bg-red-500" : 
                            task.status === "completed" ? "bg-green-500" : "bg-blue-500"
                          }`}
                          style={{ width: `${task.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                  
                  {/* 任务详情 */}
                  <div className="text-sm text-muted-foreground space-y-1">
                    <div className="flex space-x-4">
                      <span>开始时间：{task.startTime}</span>
                      {task.endTime && <span>结束时间：{task.endTime}</span>}
                      {task.duration && <span>耗时：{task.duration}</span>}
                    </div>
                    <div className="flex space-x-4">
                      {task.details.totalRecords && (
                        <span>
                          记录：{task.details.processedRecords || 0} / {task.details.totalRecords}
                        </span>
                      )}
                      {task.details.errorCount !== undefined && task.details.errorCount > 0 && (
                        <span className="text-red-600">错误：{task.details.errorCount}</span>
                      )}
                      {task.details.model && <span>模型：{task.details.model}</span>}
                      {task.details.collection && <span>Collection：{task.details.collection}</span>}
                    </div>
                  </div>
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex items-center space-x-2">
                {task.status === "running" && (
                  <>
                    <Button variant="outline" size="sm">
                      <Pause className="w-4 h-4" />
                    </Button>
                    <Button variant="destructive" size="sm">
                      <Square className="w-4 h-4" />
                    </Button>
                  </>
                )}
                {task.status === "paused" && (
                  <Button variant="outline" size="sm">
                    <Play className="w-4 h-4" />
                  </Button>
                )}
                {task.status === "failed" && (
                  <Button variant="outline" size="sm">
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                )}
                <Button variant="outline" size="sm">
                  查看日志
                </Button>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredTasks.length === 0 && (
        <Card className="p-12 text-center">
          <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">暂无任务</h3>
          <p className="text-muted-foreground">
            {filterStatus === "all" ? "还没有任何任务" : `没有${getStatusText(filterStatus as TaskStatus)}的任务`}
          </p>
        </Card>
      )}
    </div>
  );
}
