# GitHub 上传指南

## 方式 1：通过 GitHub 网页创建（推荐）

### 步骤 1：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `AffectCompanyAgent` 或 `emotion-strategies`
   - **Description**: 基于多智能体的情感陪伴系统
   - **Visibility**: Public（公开）或 Private（私有）
   - ❌ 不要勾选 "Add a README file"
   - ❌ 不要勾选 "Add .gitignore"
   - ❌ 不要勾选 "Choose a license"

3. 点击 "Create repository"

### 步骤 2：添加远程仓库并推送

创建仓库后，GitHub 会显示仓库 URL（类似 `https://github.com/your-username/AffectCompanyAgent.git`）

在项目根目录执行以下命令：

```bash
# 进入项目目录
cd E:\AI\ZJU_BJ\CUIBO\AffectCompanyAgent\emotion_strategies

# 添加远程仓库（替换为您的仓库 URL）
git remote add origin https://github.com/YOUR_USERNAME/AffectCompanyAgent.git

# 推送代码到 GitHub
git push -u origin master

# 或者如果使用 main 分支
# git branch -M main
# git push -u origin main
```

### 步骤 3：验证

访问您的 GitHub 仓库页面，刷新后应该能看到所有代码文件。

---

## 方式 2：使用 GitHub CLI（如果已安装）

```bash
# 创建仓库并推送
gh repo create AffectCompanyAgent --public --source=. --remote=origin --push
```

---

## 方式 3：使用 Git 客户端工具

如果您使用 Git 客户端工具（如 GitHub Desktop、SourceTree 等）：

1. 打开工具
2. 添加现有仓库：`E:\AI\ZJU_BJ\CUIBO\AffectCompanyAgent\emotion_strategies`
3. 在工具中创建远程仓库
4. 推送代码

---

## 常见问题

### Q: 推送失败提示权限错误？
A: 确保您已经在 GitHub 创建了仓库，并且 URL 正确。如果使用 HTTPS，可能需要输入 GitHub 用户名和 Token（不是密码）。

### Q: 如何生成 GitHub Token？
A: 
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：至少勾选 `repo`（完整仓库控制）
4. 生成后复制 Token，保存好（只会显示一次）
5. 推送时使用 Token 作为密码

### Q: 仓库太大无法推送？
A: 检查是否有大文件。本项目应该不大，如果遇到此问题，可以运行：
```bash
git count-objects -vH
```

### Q: 如何查看推送状态？
A: 
```bash
git status
git log --oneline
```

---

## 推送后的操作

### 1. 完善仓库信息

在 GitHub 仓库页面：
- 添加 Topics 标签：`ai` `emotional-support` `multi-agent` `fastapi` `llm`
- 上传项目截图或 Logo
- 完善 Website 链接（如果有部署）

### 2. 保护主分支（可选）

Settings → Branches → Add branch protection rule:
- Branch name pattern: `master` 或 `main`
- 勾选 "Require a pull request before merging"

### 3. 添加 GitHub Actions（可选）

可以添加 CI/CD 工作流自动测试和部署。

---

## 完整命令示例

```bash
# 1. 确认已在本地提交
cd E:\AI\ZJU_BJ\CUIBO\AffectCompanyAgent\emotion_strategies
git log --oneline

# 2. 添加远程仓库（替换为您的用户名）
git remote add origin https://github.com/skh-git/AffectCompanyAgent.git

# 3. 查看远程仓库
git remote -v

# 4. 推送到 GitHub
git push -u origin master

# 5. 查看推送结果
git status
```

---

## 需要帮助？

如果遇到任何问题，可以：
1. 查看 Git 错误信息
2. 访问 GitHub Docs: https://docs.github.com/
3. 检查网络连接

祝上传顺利！ 🚀