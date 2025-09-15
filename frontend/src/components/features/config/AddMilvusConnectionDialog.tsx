import { useState } from "react";
import { useAppDispatch, useAppSelector } from "@/hooks/redux";
import { createMilvusConnection, clearError } from "@/store/slices/milvusConnectionsSlice";
import type { 
  MilvusConnectionFormData, 
  MilvusConnectionValidationErrors
} from "@/types/milvusConnections";
import { validateMilvusConnectionForm, validateMilvusConnectionField } from "@/utils/validation";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Database } from "lucide-react";

// 添加连接配置对话框Props接口
interface AddMilvusConnectionDialogProps {
  onSuccess: () => void;
}

// 表单验证函数
export default function AddMilvusConnectionDialog({ onSuccess }: AddMilvusConnectionDialogProps) {
  const dispatch = useAppDispatch();
  
  // Redux 状态
  const { loading, error } = useAppSelector((state) => ({
    loading: state.milvusConnections.loading.create,
    error: state.milvusConnections.error.create,
  }));
  
  // 本地表单状态
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState<MilvusConnectionFormData>({
    name: "",
    description: "",
    uri: "",                        // 空值，显示占位符
    database_name: "",              // 空值，显示占位符
    token: "",
  });
  const [validationErrors, setValidationErrors] = useState<MilvusConnectionValidationErrors>({});
  
  // 检查表单是否完整且有效
  const errors = validateMilvusConnectionForm(formData);
  const isFormValid = Object.keys(errors).length === 0 && 
                     formData.name.trim() && formData.uri.trim() && formData.token.trim();
  
  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) {
      // 用户手动关闭对话框时清理表单
      clearForm();
      // 清除 Redux 错误状态
      dispatch(clearError('create'));
    }
  };
  
  // 清理表单数据
  const clearForm = () => {
    setFormData({
      name: "",
      description: "",
      uri: "",
      database_name: "",
      token: "",
    });
    setValidationErrors({});
  };

  // 处理表单字段变化
  const handleInputChange = (field: keyof MilvusConnectionFormData, value: string | number | boolean) => {
    const newFormData = {
      ...formData,
      [field]: value
    };
    
    setFormData(newFormData);
    
    // 实时验证：当用户修改字段时立即验证该字段
    if (field in {name: '', uri: '', database_name: '', token: ''}) {
      const fieldError = validateMilvusConnectionField(
        field as keyof MilvusConnectionValidationErrors, 
        value, 
        newFormData
      );
      
      setValidationErrors(prev => ({
        ...prev,
        [field]: fieldError
      }));
    }
  };

  // 处理保存操作
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // 阻止表单默认提交行为，防止页面跳转
    
    // 验证表单
    const currentErrors = validateMilvusConnectionForm(formData);
    setValidationErrors(currentErrors);
    
    if (Object.keys(currentErrors).length > 0 || !isFormValid) {
      return;
    }
    
    try {
      // 准备请求数据
        const requestData = {
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          uri: formData.uri.trim(),
          database_name: formData.database_name.trim(),
          token: formData.token.trim(),
        };

      // 调用 Redux action 创建连接配置
      const result = await dispatch(createMilvusConnection(requestData));
      
      // 检查是否成功
      if (createMilvusConnection.fulfilled.match(result)) {
        // 成功：清理表单，关闭对话框，调用成功回调
        clearForm();
        setIsOpen(false);
        onSuccess();
      }
      // 失败的情况由 Redux 自动处理，错误会显示在 UI 中
    } catch (err) {
      // 额外的错误处理（如果需要）
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          添加连接
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[500px] max-h-[80vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-600" />
              添加 Milvus 连接配置
            </DialogTitle>
            <DialogDescription>
              配置新的 Milvus 数据库连接。
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* 基本信息 */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground border-b pb-2">基本信息</h4>
              
              <div className="space-y-2">
                <Label htmlFor="name">
                  连接名称
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="例如：生产环境"
                  className={validationErrors.name ? "border-red-500" : ""}
                  required
                />
                {validationErrors.name && (
                  <p className="text-xs text-red-500">{validationErrors.name}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">
                  描述
                </Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="连接配置的说明，如：用户名、知识库说明等（可选）"
                  rows={2}
                />
              </div>
            </div>

            {/* 连接参数 */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground border-b pb-2">连接参数</h4>
              
              <div className="space-y-2">
                <Label htmlFor="uri">
                  连接 URI
                </Label>
                <Input
                  id="uri"
                  value={formData.uri}
                  onChange={(e) => handleInputChange('uri', e.target.value)}
                  placeholder="例如：http://localhost:19530"
                  className={validationErrors.uri ? "border-red-500" : ""}
                  required
                />
                {validationErrors.uri && (
                  <p className="text-xs text-red-500">{validationErrors.uri}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  支持本地部署（如 http://localhost:19530）或云服务（如 Zilliz Cloud）的 URI
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="database_name">
                  数据库名称
                </Label>
                <Input
                  id="database_name"
                  value={formData.database_name}
                  onChange={(e) => handleInputChange('database_name', e.target.value)}
                  placeholder="例如：default"
                  className={validationErrors.database_name ? "border-red-500" : ""}
                  required
                />
                {validationErrors.database_name && (
                  <p className="text-xs text-red-500">{validationErrors.database_name}</p>
                )}
              </div>

            </div>

            {/* 认证信息 */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground border-b pb-2">认证信息</h4>
              
              <div className="space-y-2">
                <Label htmlFor="token">
                  认证 Token
                </Label>
                <Input
                  id="token"
                  value={formData.token}
                  onChange={(e) => handleInputChange('token', e.target.value)}
                  placeholder="例如：your_token 或 username:password"
                  className={validationErrors.token ? "border-red-500" : ""}
                  autoComplete="off"
                  required
                />
                {validationErrors.token && (
                  <p className="text-xs text-red-500">{validationErrors.token}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  认证信息将加密传输并安全存储。可以是单独的 token 或 username:password 格式
                </p>
              </div>

            </div>
          </div>

          {error && <p className="text-sm text-red-500 text-center mb-4">{error}</p>}

          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">
                取消
              </Button>
            </DialogClose>

            <Button 
              type="submit" 
              disabled={!isFormValid || loading}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  创建中...
                </>
              ) : (
                "创建连接"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
