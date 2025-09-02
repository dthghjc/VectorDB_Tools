import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Plus, Trash2, Eye } from "lucide-react";

// 字段类型选项
const fieldTypes = [
  { value: "int64", label: "整数 (int64)" },
  { value: "varchar", label: "字符串 (varchar)" },
  { value: "float_vector", label: "向量 (float_vector)" },
  { value: "bool", label: "布尔值 (bool)" },
  { value: "json", label: "JSON 对象" }
];

// 字段定义接口
interface FieldDefinition {
  id: string;
  name: string;
  type: string;
  dimension?: number;
  maxLength?: number;
  isPrimary: boolean;
  description: string;
}

export default function CreateSchemaPage() {
  const [schemaName, setSchemaName] = useState("");
  const [description, setDescription] = useState("");
  const [fields, setFields] = useState<FieldDefinition[]>([
    {
      id: "1",
      name: "id",
      type: "int64",
      isPrimary: true,
      description: "主键字段"
    }
  ]);
  const [showPreview, setShowPreview] = useState(false);

  // 添加新字段
  const addField = () => {
    const newField: FieldDefinition = {
      id: Date.now().toString(),
      name: "",
      type: "varchar",
      isPrimary: false,
      description: ""
    };
    setFields([...fields, newField]);
  };

  // 删除字段
  const removeField = (fieldId: string) => {
    setFields(fields.filter(f => f.id !== fieldId));
  };

  // 更新字段
  const updateField = (fieldId: string, updates: Partial<FieldDefinition>) => {
    setFields(fields.map(f => f.id === fieldId ? { ...f, ...updates } : f));
  };

  // 生成 Schema JSON 预览
  const generateSchemaJson = () => {
    return {
      collection_name: schemaName,
      description: description,
      fields: fields.map(field => ({
        name: field.name,
        type: field.type,
        is_primary: field.isPrimary,
        dimension: field.dimension,
        max_length: field.maxLength,
        description: field.description
      }))
    };
  };

  return (
    <div className="space-y-6">
      {/* 面包屑导航 */}
      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
        <Link to="/schema" className="hover:text-foreground">
          Schema 管理
        </Link>
        <span>/</span>
        <span className="text-foreground">创建 Schema</span>
      </div>

      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">创建 Schema</h1>
          <p className="text-muted-foreground">
            定义您的 Milvus Collection 结构
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" asChild>
            <Link to="/schema">
              <ArrowLeft className="w-4 h-4 mr-2" />
              返回
            </Link>
          </Button>
          <Button variant="outline" onClick={() => setShowPreview(!showPreview)}>
            <Eye className="w-4 h-4 mr-2" />
            {showPreview ? "隐藏预览" : "预览 JSON"}
          </Button>
          <Button>
            保存 Schema
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* 主编辑区域 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 基本信息 */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">基本信息</h3>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="schemaName">Schema 名称</Label>
                <Input
                  id="schemaName"
                  value={schemaName}
                  onChange={(e) => setSchemaName(e.target.value)}
                  placeholder="例如：document_vectors"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">描述</Label>
                <Input
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="简要描述这个 Schema 的用途"
                />
              </div>
            </div>
          </Card>

          {/* 字段定义 */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">字段定义</h3>
              <Button onClick={addField} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                添加字段
              </Button>
            </div>

            <div className="space-y-4">
              {fields.map((field, index) => (
                <div key={field.id} className="border rounded-lg p-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">字段 {index + 1}</span>
                    {!field.isPrimary && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeField(field.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>字段名称</Label>
                      <Input
                        value={field.name}
                        onChange={(e) => updateField(field.id, { name: e.target.value })}
                        placeholder="字段名称"
                        disabled={field.isPrimary}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>数据类型</Label>
                      <select
                        className="w-full px-3 py-2 border border-input rounded-md"
                        value={field.type}
                        onChange={(e) => updateField(field.id, { type: e.target.value })}
                        disabled={field.isPrimary}
                      >
                        {fieldTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* 额外参数 */}
                  {field.type === "float_vector" && (
                    <div className="space-y-2">
                      <Label>向量维度</Label>
                      <Input
                        type="number"
                        value={field.dimension || ""}
                        onChange={(e) => updateField(field.id, { dimension: parseInt(e.target.value) })}
                        placeholder="例如：1536"
                      />
                    </div>
                  )}

                  {field.type === "varchar" && (
                    <div className="space-y-2">
                      <Label>最大长度</Label>
                      <Input
                        type="number"
                        value={field.maxLength || ""}
                        onChange={(e) => updateField(field.id, { maxLength: parseInt(e.target.value) })}
                        placeholder="例如：500"
                      />
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label>描述</Label>
                    <Input
                      value={field.description}
                      onChange={(e) => updateField(field.id, { description: e.target.value })}
                      placeholder="字段描述"
                    />
                  </div>

                  {field.isPrimary && (
                    <div className="bg-blue-50 p-2 rounded text-sm text-blue-700">
                      <strong>主键字段</strong> - 自动递增的唯一标识符
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* 侧边栏 - JSON 预览 */}
        {showPreview && (
          <div className="lg:col-span-1">
            <Card className="p-6 sticky top-6">
              <h3 className="text-lg font-semibold mb-4">Schema JSON 预览</h3>
              <pre className="bg-slate-100 p-4 rounded-lg text-xs overflow-auto max-h-96">
                {JSON.stringify(generateSchemaJson(), null, 2)}
              </pre>
            </Card>
          </div>
        )}
      </div>

      {/* 帮助信息 */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">字段类型说明</h3>
        <div className="text-sm text-blue-700 space-y-1">
          <p><strong>int64:</strong> 64位整数，常用于ID字段</p>
          <p><strong>varchar:</strong> 可变长度字符串，需要指定最大长度</p>
          <p><strong>float_vector:</strong> 浮点数向量，需要指定维度</p>
          <p><strong>bool:</strong> 布尔值，true 或 false</p>
          <p><strong>json:</strong> JSON 对象，用于存储复杂数据结构</p>
        </div>
      </Card>
    </div>
  );
}
