# 🚀 部署 Astro 站点到 Cloudflare Pages

## 当前状态
- ✅ Astro 代码已推送到 GitHub `andy-develop/novel-site`（main 分支，`astro/` 目录）
- ✅ 本地构建和验证全部通过
- ✅ wrangler.toml、R2 binding 配置就绪
- ❌ API Token 缺少 Pages 权限，无法命令行部署

## 方案：Cloudflare Dashboard Git 集成（1分钟）

### Step 1: 创建 Pages 项目
1. 打开 https://dash.cloudflare.com → 左侧 **Workers & Pages**
2. 点 **Create** → 选 **Pages** 标签 → **Connect to Git**
3. 连接 GitHub 账号，选择 `andy-develop/novel-site` 仓库

### Step 2: 构建设置（关键！）
填入以下值：

| 字段 | 值 |
|------|------|
| **Project name** | `novel-vault` |
| **Production branch** | `main` |
| **Build command** | `cd astro && npm ci && CF_PAGES=1 npx astro build` |
| **Build output directory** | `astro/dist` |

### Step 3: 环境变量
添加：
- `CF_PAGES` = `1`
- `NODE_VERSION` = `22`

### Step 4: 点 Save and Deploy
等待构建完成（约 2-3 分钟）

### Step 5: 绑定 R2 Bucket
1. 构建成功后 → 项目 Settings → **Bindings**
2. Add binding → **R2 Bucket**
3. Variable name: `R2_BUCKET`
4. R2 Bucket: `novel-data`
5. Save

### Step 6: 绑定自定义域名 lyriq.space
1. 项目 Settings → **Custom domains**
2. Add domain → 输入 `lyriq.space`
3. Cloudflare 会自动配置 DNS（CNAME 指向 Pages）

> ⚠️ 注意：这会替换现有的 GitHub Pages DNS 指向。原来的 Vue SPA 将不再服务。

### Step 7: 删除 GitHub Pages 的旧 workflow（可选）
部署成功后，可以去 GitHub 关闭 `deploy.yml` workflow，避免两个部署冲突。
