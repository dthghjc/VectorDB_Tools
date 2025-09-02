import { Outlet } from "react-router-dom";
import { Suspense } from "react";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { AppSidebar } from "@/components/layout/sidebar/app-sidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

export default function AppLayout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="flex h-[calc(100vh-1rem)] flex-col">
        {/* 创建一个页眉 (Header) 作为顶部导航栏 */}
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            {/* 分隔线 */}
            <div className="h-4 w-px bg-sidebar-border" />
          </div>
          
          {/* 右侧工具栏 */}
          <div className="ml-auto flex items-center gap-2 px-4">
            <LanguageSwitcher />
            <ThemeToggle />
          </div>
        </header>

        {/* 页面主要内容区域 - 设置为可滚动的容器 */}
        <div className="flex flex-1 flex-col gap-4 overflow-auto p-4 pt-0">
          <Suspense fallback={
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
                <p className="text-sm text-muted-foreground">正在加载页面...</p>
              </div>
            </div>
          }>
            <Outlet />
          </Suspense>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}