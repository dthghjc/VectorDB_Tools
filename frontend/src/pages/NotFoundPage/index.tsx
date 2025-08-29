import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center space-y-6 bg-background p-4 text-center">
      <div className="space-y-2">
        <h1 className="text-5xl font-bold tracking-tighter sm:text-7xl">404</h1>
        <p className="text-2xl font-medium text-muted-foreground">
          页面未找到
        </p>
      </div>
      <p className="max-w-md text-muted-foreground">
        抱歉，我们无法找到您正在寻找的页面。它可能已被移动或删除。
      </p>
      <Button asChild>
        <Link to="/">返回首页</Link>
      </Button>
    </div>
  );
}
