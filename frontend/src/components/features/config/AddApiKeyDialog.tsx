import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAppDispatch, useAppSelector } from "@/hooks/redux";
import { createApiKey, clearError } from "@/store/slices/apiKeysSlice";
import { validateApiKeyForm, type ApiKeyValidationErrors } from "@/utils/validation";
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
import { Plus } from "lucide-react";

// 添加密钥对话框Props接口
interface AddApiKeyDialogProps {
  onSuccess: () => void;
}

export default function AddApiKeyDialog({ onSuccess }: AddApiKeyDialogProps) {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  
  // Redux 状态
  const { loading, error } = useAppSelector((state) => ({
    loading: state.apiKeys.loading.create,
    error: state.apiKeys.error.create,
  }));
  
  // 本地表单状态
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState("");
  const [provider, setProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [validationErrors, setValidationErrors] = useState<ApiKeyValidationErrors>({});

  // 检查表单是否完整且有效
  const formData = { name, provider, apiKey, baseUrl };
  const errors = validateApiKeyForm(formData);
  const isFormValid = Object.keys(errors).length === 0 && 
                     name.trim() && provider.trim() && apiKey.trim() && baseUrl.trim();
  
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
    setName("");
    setProvider("");
    setApiKey("");
    setBaseUrl("");
    setValidationErrors({});
  };

  // 处理保存操作
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // 阻止表单默认提交行为，防止页面跳转
    
    // 验证表单
    const currentErrors = validateApiKeyForm(formData);
    setValidationErrors(currentErrors);
    
    if (Object.keys(currentErrors).length > 0 || !isFormValid) {
      return;
    }
    
    try {
      // 调用 Redux action 创建 API Key
      const result = await dispatch(createApiKey({
        name: name.trim(),
        provider: provider.trim(),
        api_key: apiKey.trim(),
        base_url: baseUrl.trim(),
      }));
      
      // 检查是否成功
      if (createApiKey.fulfilled.match(result)) {
        // 成功：清理表单，关闭对话框，调用成功回调
        clearForm();
        setIsOpen(false);
        onSuccess();
      }
      // 失败的情况由 Redux 自动处理，错误会显示在 UI 中
    } catch (err) {
      // 额外的错误处理（如果需要）
      console.error('创建 API Key 失败:', err);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          {t('addApiKeyDialog.addButton')}
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{t('addApiKeyDialog.title')}</DialogTitle>
            <DialogDescription>
              {t('addApiKeyDialog.description')}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                {t('addApiKeyDialog.nameLabel')}
              </Label>
              <div className="col-span-3 space-y-1">
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t('addApiKeyDialog.namePlaceholder')}
                  className={validationErrors.name ? "border-red-500" : ""}
                  required
                />
                {validationErrors.name && (
                  <p className="text-xs text-red-500">{validationErrors.name}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="provider" className="text-right">
                {t('addApiKeyDialog.providerLabel')}
              </Label>
              <Input
                id="provider"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                placeholder={t('addApiKeyDialog.providerPlaceholder')}
                className="col-span-3"
                required
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="apiKey" className="text-right">
                {t('addApiKeyDialog.apiKeyLabel')}
              </Label>
              <div className="col-span-3 space-y-1">
                <Input
                  id="apiKey"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={t('addApiKeyDialog.apiKeyPlaceholder')}
                  className={validationErrors.apiKey ? "border-red-500" : ""}
                  required
                />
                {validationErrors.apiKey && (
                  <p className="text-xs text-red-500">{validationErrors.apiKey}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="baseUrl" className="text-right">
                {t('addApiKeyDialog.baseUrlLabel')}
              </Label>
              <div className="col-span-3 space-y-1">
                <Input
                  id="baseUrl"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder={t('addApiKeyDialog.baseUrlPlaceholder')}
                  className={validationErrors.baseUrl ? "border-red-500" : ""}
                  required
                />
                {validationErrors.baseUrl && (
                  <p className="text-xs text-red-500">{validationErrors.baseUrl}</p>
                )}
              </div>
            </div>
          </div>

          {error && <p className="text-sm text-red-500 text-center mb-4">{error}</p>}

          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">
                {t('addApiKeyDialog.cancelButton')}
              </Button>
            </DialogClose>

            <Button 
              type="submit" 
              disabled={!isFormValid || loading}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {t('addApiKeyDialog.saving')}
                </>
              ) : (
                t('addApiKeyDialog.saveButton')
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}