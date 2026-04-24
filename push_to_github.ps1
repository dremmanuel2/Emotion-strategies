# GitHub 推送脚本
# 使用方法：.\push_to_github.ps1 -RepoUrl "https://github.com/your-username/repo.git"

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl,
    
    [ValidateSet("master", "main")]
    [string]$Branch = "master"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub 推送脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取当前目录
$projectDir = $PSScriptRoot
Set-Location $projectDir

Write-Host "项目目录：$projectDir" -ForegroundColor Yellow
Write-Host "远程仓库：$RepoUrl" -ForegroundColor Yellow
Write-Host "分支：$Branch" -ForegroundColor Yellow
Write-Host ""

# 检查是否已初始化 git
if (-not (Test-Path ".git")) {
    Write-Host "错误：未找到 .git 目录，请先运行 git init" -ForegroundColor Red
    exit 1
}

# 查看当前状态
Write-Host "检查 Git 状态..." -ForegroundColor Cyan
git status
Write-Host ""

# 添加远程仓库
Write-Host "添加远程仓库..." -ForegroundColor Cyan
git remote remove origin 2>$null  # 如果已存在先删除
git remote add origin $RepoUrl

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误：添加远程仓库失败" -ForegroundColor Red
    exit 1
}

Write-Host "远程仓库添加成功！" -ForegroundColor Green
Write-Host ""

# 查看远程仓库
Write-Host "远程仓库配置:" -ForegroundColor Cyan
git remote -v
Write-Host ""

# 推送代码
Write-Host "正在推送到 GitHub..." -ForegroundColor Cyan
Write-Host ""

git push -u origin $Branch

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  推送成功！✓" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "请访问您的 GitHub 仓库查看：" -ForegroundColor Yellow
    Write-Host "$RepoUrl" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  推送失败 ✗" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "1. 仓库不存在 - 请先在 GitHub 创建仓库" -ForegroundColor White
    Write-Host "2. 认证失败 - 检查用户名和 Token" -ForegroundColor White
    Write-Host "3. 网络问题 - 检查网络连接" -ForegroundColor White
    Write-Host ""
    Write-Host "错误信息：" -ForegroundColor Red
    git push -u origin $Branch 2>&1
    Write-Host ""
}