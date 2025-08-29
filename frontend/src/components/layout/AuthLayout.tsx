import { Outlet } from "react-router-dom";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { ThemeToggle } from "@/components/common/ThemeToggle";

export default function AuthLayout() {
  return (
    <div className="relative flex min-h-screen flex-col">
      {/* 右上角工具栏 */}
      <div className="absolute right-4 top-4 z-10 flex items-center space-x-2">
        <ThemeToggle />
        <LanguageSwitcher />
      </div>
      
      {/* 主要内容区域 */}
      <main className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
        <div className="w-full max-w-4xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}