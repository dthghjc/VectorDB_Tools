import { Outlet } from "react-router-dom";
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
      <SidebarInset>
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

        {/* 页面主要内容区域 */}
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {/* <Outlet /> */}
          {/* --- 添加下面的测试代码 --- */}
          <div>
            <h1 className="text-xl font-bold">滚动测试</h1>
            <p>如果布局正确，只有这部分内容会滚动，侧边栏和顶部栏应该固定不动。</p>
            {Array.from({ length: 100 }).map((_, i) => (
              <p key={i}>滚动项 {i + 1}</p>
            ))}
          </div>
          {/* --- 测试代码结束 --- */}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}