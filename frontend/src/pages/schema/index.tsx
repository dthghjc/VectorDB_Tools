import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { BookOpen, Plus, FileText, Clock, Database } from "lucide-react";

// 模拟的 Schema 模板数据
const mockSchemas = [
  {
    id: "1",
    name: "文档向量化模板",
    description: "适用于文档内容向量化的标准 Schema",
    fields: 5,
    vectorDim: 1536,
    lastModified: "2024-01-15",
    status: "active"
  },
  {
    id: "2", 
    name: "图片特征模板",
    description: "用于图片特征向量存储的 Schema",
    fields: 4,
    vectorDim: 2048,
    lastModified: "2024-01-12",
    status: "draft"
  },
  {
    id: "3",
    name: "商品推荐模板", 
    description: "电商商品推荐系统专用 Schema",
    fields: 8,
    vectorDim: 768,
    lastModified: "2024-01-10",
    status: "active"
  }
];

export default function SchemaPage() {
  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Schema 管理</h1>
          <p className="text-muted-foreground">
            创建、编辑和管理 Milvus Collection 的 Schema 模板
          </p>
        </div>
        <Button asChild>
          <Link to="/schema/create">
            <Plus className="w-4 h-4 mr-2" />
            创建 Schema
          </Link>
        </Button>
      </div>

      {/* 功能导航卡片 */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Plus className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold">创建 Schema</h3>
              <p className="text-sm text-muted-foreground">
                从零开始创建新的 Schema 模板
              </p>
            </div>
          </div>
          <Button asChild className="w-full mt-4">
            <Link to="/schema/create">
              开始创建
            </Link>
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold">模板库</h3>
              <p className="text-sm text-muted-foreground">
                浏览预设的 Schema 模板
              </p>
            </div>
          </div>
          <Button asChild variant="outline" className="w-full mt-4">
            <Link to="/schema/templates">
              浏览模板
            </Link>
          </Button>
        </Card>

        <Card className="p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Database className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold">从 Collection 导入</h3>
              <p className="text-sm text-muted-foreground">
                从现有 Collection 导入 Schema
              </p>
            </div>
          </div>
          <Button variant="outline" className="w-full mt-4">
            导入 Schema
          </Button>
        </Card>
      </div>

      {/* Schema 列表 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">我的 Schema ({mockSchemas.length})</h2>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              筛选
            </Button>
            <Button variant="outline" size="sm">
              排序
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {mockSchemas.map((schema) => (
            <Card key={schema.id} className="p-6 hover:shadow-md transition-shadow">
              <div className="space-y-3">
                {/* Schema 头部信息 */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="bg-indigo-100 p-2 rounded-lg">
                      <BookOpen className="h-5 w-5 text-indigo-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{schema.name}</h3>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                        schema.status === "active" 
                          ? "bg-green-100 text-green-800" 
                          : "bg-yellow-100 text-yellow-800"
                      }`}>
                        {schema.status === "active" ? "活跃" : "草稿"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Schema 描述 */}
                <p className="text-sm text-muted-foreground">
                  {schema.description}
                </p>

                {/* Schema 统计信息 */}
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{schema.fields} 个字段</span>
                  <span>{schema.vectorDim}D 向量</span>
                </div>

                {/* 最后修改时间 */}
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>最后修改：{schema.lastModified}</span>
                </div>

                {/* 操作按钮 */}
                <div className="flex space-x-2 pt-2">
                  <Button size="sm" className="flex-1">
                    编辑
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    复制
                  </Button>
                  <Button size="sm" variant="outline">
                    使用
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* 使用提示 */}
      <Card className="p-6 bg-slate-50 border-slate-200">
        <div className="flex items-start space-x-3">
          <BookOpen className="h-5 w-5 text-slate-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-slate-900">使用提示</h3>
            <p className="text-sm text-slate-700 mt-1">
              • Schema 定义了 Collection 的字段结构和数据类型<br/>
              • 向量字段的维度必须与您使用的向量模型匹配<br/>
              • 创建后的 Schema 可以在数据导入时直接使用
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
