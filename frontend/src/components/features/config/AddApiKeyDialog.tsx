import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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
  
  // --- 状态管理 ---
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState("");
  const [provider, setProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 检查表单是否完整
  const isFormValid = name.trim() && provider.trim() && apiKey.trim() && baseUrl.trim();
  
  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) {
      // 用户手动关闭对话框时清理表单
      clearForm();
    }
  };
  
  // 清理表单数据
  const clearForm = () => {
    setName("");
    setProvider("");
    setApiKey("");
    setBaseUrl("");
    setError(null);
    setIsLoading(false);
  };

  // 处理保存操作
  const handleSave = async () => {
    if (!isFormValid) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // TODO: 调用后端API保存密钥
      console.log("保存密钥:", { name, provider, apiKey, baseUrl });
      
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 成功后先清理表单，再关闭对话框
      clearForm();
      setIsOpen(false);
      onSuccess();
    } catch (err) {
      setError(t('addApiKeyDialog.saveError'));
      setIsLoading(false);
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
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('addApiKeyDialog.namePlaceholder')}
              className="col-span-3"
              required
            />
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
            <Input
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={t('addApiKeyDialog.apiKeyPlaceholder')}
              className="col-span-3"
              required
            />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="baseUrl" className="text-right">
              {t('addApiKeyDialog.baseUrlLabel')}
            </Label>
            <Input
              id="baseUrl"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder={t('addApiKeyDialog.baseUrlPlaceholder')}
              className="col-span-3"
              required
            />
          </div>
        </div>

        {error && <p className="text-sm text-red-500 text-center mb-4">{error}</p>}

        <DialogFooter>
          <Button 
            type="submit" 
            disabled={!isFormValid || isLoading}
            onClick={handleSave}
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                {t('addApiKeyDialog.saving')}
              </>
            ) : (
              t('addApiKeyDialog.saveButton')
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}