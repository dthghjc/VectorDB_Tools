import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { 
  Search, 
  FileText, 
  BarChart3, 
  Plus, 
  Play, 
  Download,
  Target
} from "lucide-react";

// 测试集数据
const mockTestSets = [
  {
    id: "1",
    name: "产品搜索测试集",
    description: "针对产品搜索场景的测试查询",
    queryCount: 50,
    lastUsed: "2024-01-15",
    status: "active"
  },
  {
    id: "2",
    name: "FAQ 问答测试",
    description: "常见问题的检索效果测试",
    queryCount: 120,
    lastUsed: "2024-01-12", 
    status: "active"
  },
  {
    id: "3",
    name: "语义相似度评估",
    description: "测试模型的语义理解能力",
    queryCount: 80,
    lastUsed: "2024-01-10",
    status: "draft"
  }
];

// 最近的评估结果
const recentEvaluations = [
  {
    id: "1",
    name: "产品搜索性能测试",
    testSet: "产品搜索测试集",
    collection: "product_vectors",
    status: "completed",
    accuracy: 85.6,
    avgResponseTime: 45,
    totalQueries: 50,
    createdAt: "2024-01-15 14:30:00"
  },
  {
    id: "2",
    name: "FAQ 检索效果评估",
    testSet: "FAQ 问答测试",
    collection: "faq_knowledge",
    status: "running",
    progress: 65,
    totalQueries: 120,
    createdAt: "2024-01-15 16:20:00"
  },
  {
    id: "3",
    name: "多模型对比测试",
    testSet: "语义相似度评估",
    collection: "mixed_content",
    status: "failed",
    accuracy: 0,
    totalQueries: 80,
    createdAt: "2024-01-15 12:10:00"
  }
];

export default function SearchEvalPage() {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-100";
      case "running":
        return "text-blue-600 bg-blue-100";
      case "failed":
        return "text-red-600 bg-red-100";
      case "active":
        return "text-green-600 bg-green-100";
      case "draft":
        return "text-gray-600 bg-gray-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "已完成";
      case "running":
        return "运行中";
      case "failed":
        return "失败";
      case "active":
        return "活跃";
      case "draft":
        return "草稿";
      default:
        return "未知";
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">检索与评估中心</h1>
        <p className="text-muted-foreground">
          验证和测试向量数据的检索效果，评估系统性能
        </p>
      </div>

      {/* 功能导航 */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold">测试集管理</h3>
              <p className="text-sm text-muted-foreground">
                创建和管理检索测试的查询集合
              </p>
            </div>
          </div>
          <Button asChild className="w-full mt-4">
            <Link to="/search-eval/testsets">
              <FileText className="w-4 h-4 mr-2" />
              管理测试集
            </Link>
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <Search className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold">批量检索</h3>
              <p className="text-sm text-muted-foreground">
                执行大规模的批量检索测试
              </p>
            </div>
          </div>
          <Button asChild variant="outline" className="w-full mt-4">
            <Link to="/search-eval/batch">
              <Play className="w-4 h-4 mr-2" />
              开始测试
            </Link>
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-purple-100 p-3 rounded-lg">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold">结果分析</h3>
              <p className="text-sm text-muted-foreground">
                查看和分析检索测试结果
              </p>
            </div>
          </div>
          <Button asChild variant="outline" className="w-full mt-4">
            <Link to="/search-eval/results">
              <BarChart3 className="w-4 h-4 mr-2" />
              查看结果
            </Link>
          </Button>
        </Card>
      </div>

      {/* 快速开始评估 */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">快速开始评估</h2>
            <p className="text-muted-foreground text-sm">
              选择测试集和 Collection，立即开始检索性能评估
            </p>
          </div>
          <Button>
            <Play className="w-4 h-4 mr-2" />
            新建评估
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <label className="text-sm font-medium">选择测试集</label>
            <select className="w-full px-3 py-2 border border-input rounded-md">
              <option>产品搜索测试集 (50 查询)</option>
              <option>FAQ 问答测试 (120 查询)</option>
              <option>语义相似度评估 (80 查询)</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">目标 Collection</label>
            <select className="w-full px-3 py-2 border border-input rounded-md">
              <option>product_vectors</option>
              <option>faq_knowledge</option>
              <option>mixed_content</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Top-K 设置</label>
            <select className="w-full px-3 py-2 border border-input rounded-md">
              <option>5</option>
              <option>10</option>
              <option>20</option>
              <option>50</option>
            </select>
          </div>
        </div>
      </Card>

      {/* 测试集列表 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">我的测试集 ({mockTestSets.length})</h2>
          <Button asChild>
            <Link to="/search-eval/testsets">
              <Plus className="w-4 h-4 mr-2" />
              创建测试集
            </Link>
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {mockTestSets.map((testSet) => (
            <Card key={testSet.id} className="p-6">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="bg-orange-100 p-2 rounded-lg">
                      <Target className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{testSet.name}</h3>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(testSet.status)}`}>
                        {getStatusText(testSet.status)}
                      </span>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground">
                  {testSet.description}
                </p>

                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{testSet.queryCount} 个查询</span>
                  <span>最后使用：{testSet.lastUsed}</span>
                </div>

                <div className="flex space-x-2 pt-2">
                  <Button size="sm" className="flex-1">
                    编辑
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    使用
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* 最近的评估结果 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">最近的评估结果</h2>
          <Button variant="outline" asChild>
            <Link to="/search-eval/results">
              查看全部结果
            </Link>
          </Button>
        </div>

        <div className="space-y-3">
          {recentEvaluations.map((evaluation) => (
            <Card key={evaluation.id} className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-indigo-100 p-3 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{evaluation.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      测试集：{evaluation.testSet} • Collection：{evaluation.collection}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      创建时间：{evaluation.createdAt}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  {/* 进度或结果 */}
                  {evaluation.status === "running" ? (
                    <div className="text-center">
                      <div className="text-sm text-muted-foreground mb-1">进度</div>
                      <div className="text-lg font-semibold text-blue-600">{evaluation.progress}%</div>
                    </div>
                  ) : evaluation.status === "completed" ? (
                    <>
                      <div className="text-center">
                        <div className="text-sm text-muted-foreground mb-1">准确率</div>
                        <div className="text-lg font-semibold text-green-600">{evaluation.accuracy}%</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-muted-foreground mb-1">平均响应时间</div>
                        <div className="text-lg font-semibold">{evaluation.avgResponseTime}ms</div>
                      </div>
                    </>
                  ) : null}

                  <div className="text-center">
                    <div className="text-sm text-muted-foreground mb-1">查询数</div>
                    <div className="text-lg font-semibold">{evaluation.totalQueries}</div>
                  </div>

                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(evaluation.status)}`}>
                    {getStatusText(evaluation.status)}
                  </span>

                  <div className="flex space-x-2">
                    {evaluation.status === "completed" && (
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        导出
                      </Button>
                    )}
                    <Button variant="outline" size="sm">
                      查看详情
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* 使用提示 */}
      <Card className="p-6 bg-cyan-50 border-cyan-200">
        <div className="flex items-start space-x-3">
          <Search className="h-5 w-5 text-cyan-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-cyan-900">评估指南</h3>
            <div className="text-sm text-cyan-700 mt-1 space-y-1">
              <p>• <strong>测试集：</strong>建议每个测试集包含 50-200 个代表性查询</p>
              <p>• <strong>评估指标：</strong>支持准确率、召回率、响应时间等多种指标</p>
              <p>• <strong>结果导出：</strong>可导出详细的检索结果用于离线分析</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
