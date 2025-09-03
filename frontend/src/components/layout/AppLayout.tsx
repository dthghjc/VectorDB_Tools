import { Outlet, useLocation, Link } from "react-router-dom";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { AppSidebar } from "@/components/layout/sidebar/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

// 路由配置：定义每个路径的显示名称
const routeConfig: Record<string, string> = {
  '/': '首页',
  '/config': '配置中心',
  '/config/milvus': 'Milvus 配置',
  '/config/api-keys': 'API 密钥',
  '/schema': 'Schema 管理',
  '/schema/create': '创建 Schema',
  '/data-import': '数据导入',
  '/tasks': '任务中心',
  '/search-eval': '检索评估',
};

export default function AppLayout() {
  const location = useLocation();
  
  // 解析当前路径为面包屑数组
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    
    // 如果是根路径，不显示面包屑
    if (pathSegments.length === 0) {
      return [];
    }
    
    const breadcrumbs = [];
    let currentPath = '';
    
    // 构建每个层级的路径和显示名
    for (const segment of pathSegments) {
      currentPath += `/${segment}`;
      const label = routeConfig[currentPath] || segment;
      
      breadcrumbs.push({
        path: currentPath,
        label,
        isLast: currentPath === location.pathname,
      });
    }
    
    return breadcrumbs;
  };
  
  const breadcrumbs = generateBreadcrumbs();
  
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="flex h-[calc(100vh-1rem)] flex-col">
        {/* 创建一个页眉 (Header) 作为顶部导航栏 */}
        <header className="flex h-16 shrink-0 items-center gap-2">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            {/* 动态面包屑导航 */}
            {breadcrumbs.length > 0 && (
              <Breadcrumb>
                <BreadcrumbList>
                  {breadcrumbs.map((crumb, index) => (
                    <div key={crumb.path} className="flex items-center">
                      {index > 0 && <BreadcrumbSeparator className="hidden md:block" />}
                      <BreadcrumbItem className={index === 0 ? "hidden md:block" : ""}>
                        {crumb.isLast ? (
                          <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                        ) : (
                          <BreadcrumbLink asChild>
                            <Link to={crumb.path}>{crumb.label}</Link>
                          </BreadcrumbLink>
                        )}
                      </BreadcrumbItem>
                    </div>
                  ))}
                </BreadcrumbList>
              </Breadcrumb>
            )}
          </div>
          
          {/* 右侧工具栏 */}
          <div className="ml-auto flex items-center gap-2 px-4">
            <LanguageSwitcher />
            <ThemeToggle />
          </div>
        </header>

        {/* 页面主要内容区域 - 设置为可滚动的容器 */}
        <div className="flex flex-1 flex-col gap-4 overflow-auto p-4 pt-0">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}