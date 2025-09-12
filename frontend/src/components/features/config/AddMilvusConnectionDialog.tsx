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
    host: "",                       // 空值，显示占位符
    port: 0,                        // 空值，显示占位符
    database_name: "",              // 空值，显示占位符
    username: "",
    password: "",
  });
  const [validationErrors, setValidationErrors] = useState<MilvusConnectionValidationErrors>({});
  
  // 检查表单是否完整且有效
  const errors = validateMilvusConnectionForm(formData);
  const isFormValid = Object.keys(errors).length === 0 && 
                     formData.name.trim() && formData.host.trim() && formData.port > 0;
  
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
      host: "",
      port: 0,
      database_name: "",
      username: "",
      password: "",
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
    if (field in {name: '', host: '', port: 0, database_name: '', username: '', password: ''}) {
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
          host: formData.host.trim(),
          port: formData.port,
          database_name: formData.database_name.trim(),
          username: formData.username.trim(),
          password: formData.password.trim(),
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
      console.error('创建 Milvus 连接配置失败:', err);
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
              配置新的 Milvus 数据库连接。认证信息将被安全加密存储。
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* 基本信息 */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground border-b pb-2">基本信息</h4>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="name" className="text-right">
                  连接名称
                </Label>
                <div className="col-span-3 space-y-1">
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
              </div>

              <div className="grid grid-cols-4 items-start gap-4">
                <Label htmlFor="description" className="text-right pt-2">
                  描述
                </Label>
                <div className="col-span-3 space-y-1">
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="连接配置的说明（可选）"
                    rows={2}
                  />
                </div>
              </div>
            </div>

            {/* 连接参数 */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground border-b pb-2">连接参数</h4>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="host" className="text-right">
                  主机地址
                </Label>
                <div className="col-span-3 space-y-1">
                  <Input
                    id="host"
                    value={formData.host}
                    onChange={(e) => handleInputChange('host', e.target.value)}
                      placeholder="例如：http://localhost 或 https://example.com"
                    className={validationErrors.host ? "border-red-500" : ""}
                    required
                  />
                  {validationErrors.host && (
                    <p className="text-xs text-red-500">{validationErrors.host}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="port" className="text-right">
                  端口
                </Label>
                <div className="col-span-3 space-y-1">
                  <Input
                    id="port"
                    type="number"
                    value={formData.port || ""}
                    onChange={(e) => handleInputChange('port', parseInt(e.target.value) || 0)}
                    placeholder="例如：19530"
                    min="1"
                    max="65535"
                    className={validationErrors.port ? "border-red-500" : ""}
                    required
                  />
                  {validationErrors.port && (
                    <p className="text-xs text-red-500">{validationErrors.port}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="database_name" className="text-right">
                  数据库名称
                </Label>
                <div className="col-span-3 space-y-1">
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

            </div>

            {/* 认证信息 */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground border-b pb-2">认证信息</h4>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="username" className="text-right">
                  用户名
                </Label>
                <div className="col-span-3 space-y-1">
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    placeholder="例如：admin"
                    className={validationErrors.username ? "border-red-500" : ""}
                    autoComplete="username"
                    required
                  />
                  {validationErrors.username && (
                    <p className="text-xs text-red-500">{validationErrors.username}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="password" className="text-right">
                  密码
                </Label>
                <div className="col-span-3 space-y-1">
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    placeholder="例如：your_password"
                    className={validationErrors.password ? "border-red-500" : ""}
                    autoComplete="new-password"
                    required
                  />
                  {validationErrors.password && (
                    <p className="text-xs text-red-500">{validationErrors.password}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    认证信息将使用 RSA 加密传输并安全存储
                  </p>
                </div>
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
