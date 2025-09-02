"use client"

import * as React from "react"
import {
  BookOpen,
  Bot,
  Command,
  Frame,
  LifeBuoy,
  Map,
  PieChart,
  Send,
  Settings2,
  SquareTerminal,
} from "lucide-react"

import { NavMain } from "@/components/layout/sidebar/nav-main"
import { NavProjects } from "@/components/layout/sidebar/nav-projects"
import { NavSecondary } from "@/components/layout/sidebar/nav-secondary"
import { NavUser } from "@/components/layout/sidebar/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: "Admin",
    email: "admin@vectordb.tools",
    avatar: "/avatars/admin.jpg",
  },
  navMain: [
    {
      title: "配置中心",
      url: "/config",
      icon: Settings2,
      isActive: true,
      items: [
        {
          title: "Milvus 连接",
          url: "/config/milvus",
        },
        {
          title: "API 密钥",
          url: "/config/api-keys",
        },
      ],
    },
    {
      title: "Schema 管理",
      url: "/schema",
      icon: BookOpen,
      items: [
        {
          title: "创建 Schema",
          url: "/schema/create",
        },
        {
          title: "模板库",
          url: "/schema/templates",
        },
      ],
    },
    {
      title: "数据导入",
      url: "/data-import",
      icon: Bot,
      items: [
        {
          title: "上传文件",
          url: "/data-import/upload",
        },
        {
          title: "向量化",
          url: "/data-import/vectorize",
        },
        {
          title: "加载数据",
          url: "/data-import/load",
        },
      ],
    },
    {
      title: "任务中心",
      url: "/tasks",
      icon: SquareTerminal,
      items: [
        {
          title: "任务列表",
          url: "/tasks/list",
        },
        {
          title: "执行历史",
          url: "/tasks/history",
        },
      ],
    },
    {
      title: "检索评估",
      url: "/search-eval",
      icon: PieChart,
      items: [
        {
          title: "测试集管理",
          url: "/search-eval/testsets",
        },
        {
          title: "批量检索",
          url: "/search-eval/batch",
        },
        {
          title: "结果分析",
          url: "/search-eval/results",
        },
      ],
    },
  ],
  navSecondary: [
    {
      title: "Support",
      url: "#",
      icon: LifeBuoy,
    },
    {
      title: "Feedback",
      url: "#",
      icon: Send,
    },
  ],
  projects: [
    {
      name: "Design Engineering",
      url: "#",
      icon: Frame,
    },
    {
      name: "Sales & Marketing",
      url: "#",
      icon: PieChart,
    },
    {
      name: "Travel",
      url: "#",
      icon: Map,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="#">
                <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                  <Command className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">VectorDB Tools</span>
                  <span className="truncate text-xs">数据处理平台</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
