import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return (
    // 这是一个非常简洁的布局，只负责提供一个背景和居中环境
    // 所有认证相关的页面（登录、注册等）都会被渲染到这里
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-4 dark:bg-gray-950">
      <div className="w-full max-w-4xl">
        <Outlet />
      </div>
    </main>
  );
}