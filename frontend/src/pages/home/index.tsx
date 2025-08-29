import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 text-center">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl">
          欢迎来到首页
        </h1>
        <p className="max-w-[600px] text-muted-foreground md:text-xl">
          您已成功登录。这里是您的应用主界面。
        </p>
        {/* 假设未来会有一个登出功能 */}
        <Button asChild>
          <Link to="/login">
            返回登录页 (或登出)
          </Link>
        </Button>
      </div>
    </div>
  );
}
