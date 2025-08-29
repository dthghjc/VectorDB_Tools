import { Outlet } from "react-router-dom";
import { ThemeToggle } from "@/components/common/ThemeToggle";

export default function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* 2. 创建一个页眉 (Header) 作为顶部导航栏 */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          {/* 这是一个伸缩容器，它会占据所有可用空间 */}
          <div className="flex flex-1 items-center justify-end space-x-4">
            <nav className="flex items-center space-x-1">
              <ThemeToggle />
            </nav>
          </div>
        </div>
      </header>

      {/* 页面主要内容区域 */}
      <main className="flex-1 p-4">
        <Outlet />
      </main>
    </div>
  );
}