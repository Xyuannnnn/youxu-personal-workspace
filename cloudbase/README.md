# CloudBase 接入准备（未上线）

## 2026-09-13 当前进度（优先于下方准备清单）

- 用户已执行初始化，截图确认 gradlife_workspaces 表存在、RLS 两项为 true、策略数为3。不要重复执行初始化脚本。
- 邮箱登录测试入口：`http://localhost:4173/cloud.html`。原 `index.html` 继续使用本机数据。
- `src/cloud-entry.js` 使用锁定版本 @cloudbase/js-sdk 3.4.8；发码后通过返回的 verifyOtp 回调校验，登录 shouldCreateUser=false、注册=true，不使用魔法链接或 ChatGPT 登录。
- 会话采用 session 存储，业务数据只存在当前页面内存和云端；不会读取或迁移本机工作台。使用官方 PostgreSQL REST 路径 `/v1/rdb/rest/gradlife_workspaces`，携带登录用户的 access_token，禁止用 Publishable Key 代替用户令牌。
- 保存等待服务器返回确认；更新带 owner_id 与旧 version 条件，冲突/网络失败显示未保存并保留失败快照，可导出草稿。其他设备修改后需手动“刷新云端”。不承诺实时推送或自动合并。
- 云端 PDF 上传尚未启用：需要配置与验证私有文件存储后再接通；本机 PDF 功能保留，不能假装同步了文件。
- 云端实际 OTP 收信、账号隔离及保存链路尚待用户实际登录验收。尚未发布外网，不可分发 localhost 给朋友。
- 构建：`npm ci --ignore-scripts` 后 `npm run build:cloud`；`dist` 中 app.js / attachments.js / HTML / CSS 是手写源码，不能清空 dist。cloud-entry.js 是生成文件。
- 公开配置仍标记 enabled=false，表示未通过上线验收；显式测试入口使用该配置，不自动替换本机入口。

环境：gradlife-d4g72mcrq3cf4a71f；用户提供的客户端 JWT issuer 指向 ap-shanghai（上海），尚未联网验证签名或服务可用性。

邮箱验证码已由用户控制台截图确认“已启用、代发”。此目录不是已部署后端。

## 文件

- migrations/001_workspace.sql：待审查、待执行的 PostgreSQL 建表与权限脚本。不要重复执行；不修改平台 auth schema。
- client-config.example.json：仅允许公开客户端配置，不得填入 service_role 或管理员密钥。
- client-config.json：已保存用户提供的公开 Publishable Key；移除了消息中的 Markdown 转义反斜杠。enabled=false，尚未接入运行中的工作台。

## 当前准备范围

先以每账号一个带版本的 JSON 文档兼容原型，再逐步拆分业务实体。RLS 限制用户只能读写本人行；前端必须对版本冲突停止提交，保留草稿并要求合并或重新加载，不得自动覆盖。

登录接入需核实 SDK 初始化示例及允许访问的网站域名。客户端公开密钥已收到并完成本地格式/claims 检查；控制台浏览器读取曾两次超时，未向云端执行任何 SQL。

## 上线前必须完成

1. 核实客户端 SDK 版本与 auth/rdb API，接入邮箱登录/注册及退出。
2. 审查并执行 SQL，使用两账号和匿名身份验证权限与并发冲突。
3. 云端专用入口登录前不加载个人 state；新用户为空状态，退出清理缓存。
4. 将原同步 save() 改造成明确的异步保存状态，禁止先报“已保存”再后台失败。
5. 接入私有附件存储策略及上传/下载鉴权；不能仅同步 IndexedDB 文件ID。
6. 本机数据迁移需用户确认归属，先备份；不自动上传当前浏览器数据到新账号。
7. 测试 QQ/163 实际收信与验证码错误、过期、限流、恢复。
8. 才能部署给朋友试用，当前仍不可当作多人正式版。

## 参考

https://docs.cloudbase.net/authentication-v2/auth/auth-pg
https://docs.cloudbase.net/database/postgresql/connecting-to-postgresql
https://docs.cloudbase.net/authentication-v2/method/email-login
