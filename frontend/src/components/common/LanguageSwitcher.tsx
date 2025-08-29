import { useTranslation } from "react-i18next";
import { Languages } from "lucide-react";
import { Button } from "@/components/ui/button";

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const currentLang = i18n.language;
    const newLang = currentLang === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(newLang);
  };



  const getCurrentLabel = () => {
    return i18n.language === 'zh' ? 'ZH' : 'EN';
  };

  const getTooltip = () => {
    return i18n.language === 'zh' ? '切换到英文' : 'Switch to Chinese';
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleLanguage}
      title={getTooltip()}
      className="h-9 w-auto px-2 gap-1"
    >
      <Languages className="h-3 w-3" />
      <span className="text-xs font-medium">{getCurrentLabel()}</span>
      <span className="sr-only">{getTooltip()}</span>
    </Button>
  );
}
