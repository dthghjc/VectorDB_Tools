import { Outlet } from "react-router-dom";
// 这是一个示例导入，您可以未来在这里添加您的导航栏或侧边栏组件
// import Navbar from "@/components/common/Navbar"; 

export default function AppLayout() {
  return (
    // 您可以把这里想象成您应用的主框架
    <div className="flex min-h-screen flex-col">
      
      {/* 在这里可以放置您未来的顶部导航栏 */}
      {/* <Navbar /> */}
      
      {/* <main> 标签通常用来包裹页面的主要内容 */}
      <main className="flex-1">
        {/* <Outlet /> 是一个占位符，
            所有嵌套在 AppLayout 下的子路由 (如 HomePage) 
            都会被渲染到这个位置。
        */}
        <Outlet />
      </main>

      {/* 在这里可以放置您未来的页脚 */}
      {/* <footer>Footer content</footer> */}

    </div>
  );
}

