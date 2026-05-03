# 版本号与 GitHub Release 流程

## 推荐版本号策略

当前项目建议使用语义化版本风格的简化形式：

- `v0.1.0`：首个可公开分发版本
- `v0.1.1`：小修复版本
- `v0.2.0`：新增一批可感知功能，但整体架构不重做
- `v1.0.0`：产品能力和发布流程都相对稳定后的正式版

## 什么时候升版本

### Patch：`v0.1.0 -> v0.1.1`
适用于：
- 修复导入失败
- 修复图表异常
- 修复日志或导出问题
- 文案微调
- 不改变主要使用方式的小修复

### Minor：`v0.1.0 -> v0.2.0`
适用于：
- 新增一类处理能力
- 新增新的导出方式
- 新增新手引导的重要能力
- 改进 UI 布局并影响用户操作体验

### Major：`v0.x -> v1.0.0`
适用于：
- 项目定位稳定
- 核心功能完整
- 发布流程成熟
- 用户可长期使用，且兼容性预期更明确

## 当前发布产物规则

本项目当前采用 **PyInstaller 目录版发布**。

因此 GitHub Release 中应上传：

- **整个目录的 zip 包**

不应上传：

- 单独的 `desktop-data-analyzer.exe`

原因：

- exe 依赖 `_internal/` 目录中的 DLL、Qt 插件、Python 扩展与资源文件
- 单独分发 exe 会导致用户运行失败或功能缺失

推荐发布包命名：

```text
desktop-data-analyzer-exe-v0.1.0-windows.zip
```

后续版本按同样规则递增。

## 每次发版前检查清单

1. 运行全部测试

```powershell
python -m pytest -v
```

2. 重建 exe

```powershell
python scripts/build_exe.py
```

3. 确认产物目录存在

```text
dist/desktop-data-analyzer/
```

4. 手动检查：
- `desktop-data-analyzer.exe` 可以启动
- 可以导入 `.xlsx`
- 可以导入 `.xls`
- 可以执行处理
- 可以导出结果
- 新手引导可以打开
- `logs/runtime.log` 能生成

5. 压缩整个目录，而不是单独压缩 exe

## 推荐发布流程

### 1. 确认工作区干净

```powershell
git status --short
```

### 2. 提交当前修改

```powershell
git add <files>
git commit -m "feat: ..."
```

### 3. 推送主分支

```powershell
git push
```

### 4. 创建版本标签

```powershell
git tag v0.1.1
git push origin v0.1.1
```

### 5. 压缩发布目录

```powershell
Compress-Archive -Path "dist/desktop-data-analyzer/*" -DestinationPath "dist/desktop-data-analyzer-exe-v0.1.1-windows.zip" -Force
```

### 6. 创建 GitHub Release

```powershell
gh release create v0.1.1 "dist/desktop-data-analyzer-exe-v0.1.1-windows.zip" --title "v0.1.1"
```

如果上传大文件时网络不稳定，也可以分两步：

```powershell
gh release create v0.1.1 --title "v0.1.1"
gh release upload v0.1.1 "dist/desktop-data-analyzer-exe-v0.1.1-windows.zip"
```

## README 应保持同步的内容

每次发版后，建议同步检查 README 中这些内容是否仍然正确：

- 最新 Release 下载文件名
- 是否仍然是目录版发布
- 截图是否反映当前界面
- 功能列表是否与当前版本一致
- 日志路径说明是否变化

## 当前项目建议

就这个项目目前阶段而言，建议继续使用：

- `v0.x.y` 版本线
- 目录版 zip 发布
- 修复类更新走 patch
- 明显功能增长走 minor

等到功能边界更稳定、README 和发布流程不再频繁变化时，再考虑进入 `v1.0.0`。
