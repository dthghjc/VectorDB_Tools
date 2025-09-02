import { Outlet } from "react-router-dom";
import { Suspense } from "react";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { ThemeToggle } from "@/components/common/ThemeToggle";

export default function AuthLayout() {
  return (
    <div className="relative flex min-h-screen flex-col">
      {/* 右上角工具栏 */}
      <div className="absolute right-4 top-4 z-10 flex items-center space-x-1">
        <LanguageSwitcher />
        <ThemeToggle />
      </div>
      
      {/* 主要内容区域 */}
      <main className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
        <div className="w-full max-w-4xl">
          <Suspense fallback={
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
                <p className="text-sm text-muted-foreground">Loading...</p>
              </div>
            </div>
          }>
            <Outlet />
          </Suspense>
        </div>
      </main>
    </div>
  );
}