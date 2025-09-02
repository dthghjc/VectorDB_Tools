import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <>
      {/* 欢迎区域 */}
      <div className="rounded-lg border bg-card p-6 text-center">
        <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl">
          欢迎来到首页
        </h1>
        <p className="mt-4 text-muted-foreground md:text-xl">
          您已成功登录。这里是您的应用主界面。
        </p>
        <div className="mt-6">
          <Button asChild>
            <Link to="/login">
              返回登录页 (或登出)
            </Link>
          </Button>
        </div>
      </div>

      {/* 功能预览区域 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-semibold">配置中心</h3>
          <p className="text-sm text-muted-foreground">管理 Milvus 连接和 API 密钥</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-semibold">Schema 管理</h3>
          <p className="text-sm text-muted-foreground">创建和编辑 Collection 模板</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-semibold">数据导入</h3>
          <p className="text-sm text-muted-foreground">上传、向量化、加载数据流水线</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-semibold">任务中心</h3>
          <p className="text-sm text-muted-foreground">监控后台任务执行状态</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-semibold">检索评估</h3>
          <p className="text-sm text-muted-foreground">测试和验证向量检索效果</p>
        </div>
      </div>
    </>
  );
}
