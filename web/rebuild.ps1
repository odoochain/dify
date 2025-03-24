# 清理 pnpm 缓存
Write-Host "正在清理 pnpm 缓存..." -ForegroundColor Cyan
pnpm store prune

# 删除 node_modules 文件夹
Write-Host "正在删除 node_modules 文件夹..." -ForegroundColor Cyan
if (Test-Path -Path "node_modules") {
    Remove-Item -Path "node_modules" -Recurse -Force
    Write-Host "node_modules 文件夹已删除" -ForegroundColor Green
} else {
    Write-Host "node_modules 文件夹不存在，跳过删除" -ForegroundColor Yellow
}

# 询问是否使用淘宝源（默认是）
$useNpmMirror = Read-Host "是否使用淘宝源安装依赖？(Y/n)，默认使用淘宝源"
if ($useNpmMirror -ne "n" -and $useNpmMirror -ne "N") {
    Write-Host "将使用淘宝源安装依赖..." -ForegroundColor Cyan
    pnpm config set registry https://registry.npmmirror.com
    Write-Host "已设置为淘宝源" -ForegroundColor Green
}

# 重新安装依赖
Write-Host "正在重新安装依赖..." -ForegroundColor Cyan
pnpm install

# 如果使用了淘宝源，安装完成后恢复默认源
if ($useNpmMirror -ne "n" -and $useNpmMirror -ne "N") {
    Write-Host "恢复默认 npm 源..." -ForegroundColor Cyan
    pnpm config set registry https://registry.npmjs.org
    Write-Host "已恢复默认源" -ForegroundColor Green
}

# 构建项目
Write-Host "正在构建项目..." -ForegroundColor Cyan
pnpm run build

Write-Host "所有操作已完成！" -ForegroundColor Green