/*
frontend/api/ (负责 “请求什么”)

职责: 定义具体的、按功能划分的 API 请求函数。

内容:

这个目录下的每个文件都对应后端的一个资源或一个功能模块，例如 connection.ts, collection.ts。

这些文件会 导入 lib/axios.ts 中创建的那个 Axios 实例。

然后，它们导出具体的异步函数，供 UI 组件或 Redux Thunks 调用。

把它想象成: 一个功能明确的 “API 函数库”。每个函数都代表一次与后端的具体交互。

*/