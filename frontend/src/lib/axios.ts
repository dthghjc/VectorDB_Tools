/*
frontend/lib/axios.ts (负责 “如何” 请求)

职责: 创建和配置 全局唯一 的 Axios 实例。

内容:

axios.create(): 设置基础 URL (baseURL)，比如 http://localhost:8000/api/v1。

拦截器 (Interceptors): 在这里统一处理所有请求的共性问题。例如：

请求拦截器: 在每个请求头里自动添加 Authorization token (如果未来有用户登录功能)。

响应拦截器: 统一处理 API 错误，比如 401 未授权跳转到登录页，500 服务器错误弹出全局提示等。

把它想象成: 项目的“网络总管道”。它定义了所有 API 请求的出口、规则和默认行为。
*/
