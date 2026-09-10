# 主页维护说明

网站：[haoyuwang.com](https://haoyuwang.com/)。

日常内容分别放在 `_includes/homepage/` 下的 intro、news、pub、others 文件。
可复用片段不要放进 `_pages/`，否则可能被生成为独立页面并进入 sitemap。

- 修改论文时核对正式会议／期刊状态、作者顺序和 Google Scholar 论文 ID。
- 页面展示精选论文；完整列表链接到 Google Scholar。
- 新增论文图后运行 `scripts/optimize_images.py`，提交响应式 WebP 图片与生成的尺寸数据，保留原始 PNG。
- 前端使用原生 JavaScript，无需维护压缩脚本或运行打包工具。
- 推送前运行 Node 测试、Python 测试、Jekyll 构建和 `scripts/check_site.py`。
- 引用更新失败时会保留旧数据。先看 Get Citation Data 日志，区分依赖错误、网络／代理失败和数据校验失败。
- 网页依次尝试原始数据、GitHub 官方文件接口和 jsDelivr；官方接口限流时会继续尝试 CDN。CDN 分支缓存可能延迟最多 12 小时，优先使用默认的原始数据源。
- Pages 发布成功与引用更新成功是两项独立状态。
- Ruby、Bundler、Python 版本及完整命令见[仓库 README](../README.md)。

原模板的介绍和许可证归属见 README 的 Credits 以及仓库 LICENSE。
