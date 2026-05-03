# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库当前状态

当前仓库已经实现出一个可运行的 Python 桌面数据分析器原型，并补齐了测试、示例数据、PyInstaller 目录版打包配置，以及基础开发命令说明。

它对应 `项目描述.md` 中的第一阶段落地目标，当前已覆盖的核心能力包括：
- 读取本地 Excel 文件
- 在本地完成去空行、去重、筛选、排序和计算列处理
- 展示原始数据与处理结果表格
- 生成基础柱状图和折线图
- 导出处理结果为 Excel
- 构建目录版 Windows `.exe`

## 常用命令

### 安装依赖
```powershell
pip install -r requirements.txt
```

### 启动桌面程序
```powershell
python main.py
```

### 运行全部测试
```powershell
python -m pytest -v
```

### 运行单个测试
```powershell
python -m pytest tests/ui/test_main_window.py -v
```

### 构建目录版 exe
```powershell
python scripts/build_exe.py
```

构建输出会生成在 `dist/desktop-data-analyzer/` 目录下。

## 高层架构

### 入口与启动
- `main.py`：程序入口，只负责调用启动函数。
- `app/bootstrap.py`：创建 `QApplication` 和主窗口，作为桌面程序的启动层。

### 状态与界面
- `app/state.py`：集中保存当前导入文件、原始数据、处理结果、可用列、状态文案和导出路径。
- `ui/main_window.py`：主工作台窗口，串联导入、处理、图表刷新、重置和导出流程。
- `ui/panels.py`：左侧控制面板和图表承载面板。
- `ui/table_model.py`：把 pandas DataFrame 适配为 Qt 表格模型。

### 数据与图表服务
- `services/excel/io.py`：负责 Excel 首个工作表读取和结果导出。
- `services/transform/operations.py`：负责本地数据处理操作，如去空行、去重、筛选、排序和计算列。
- `services/chart/render.py`：负责图表序列准备、图表绘制和空状态绘制。

### 测试与样例
- `tests/`：覆盖表格模型、主窗口流程、Excel 读写、数据处理和图表渲染。
- `sample_data/demo_sales.xlsx`：用于手动演示和测试验证的样例数据。

### 打包层
- `desktop-data-analyzer.spec`：PyInstaller 目录版构建配置。
- `scripts/build_exe.py`：统一调用 PyInstaller 的构建脚本。

## 当前实现边界

当前版本是一个轻量可运行原型，不包含复杂业务规则配置、多工作表工作流、批量任务编排或高级图表能力。新增功能时，优先沿着现有的“单窗口 + 本地 DataFrame 处理 + 独立服务模块”结构继续扩展，不要把业务逻辑直接塞进 UI 事件代码里。

## 当前事实来源

产品目标以 `项目描述.md` 为起点，当前代码实现、测试和打包方式以仓库里的现有 Python 源码、`tests/`、`requirements.txt`、`desktop-data-analyzer.spec` 和 `scripts/build_exe.py` 为准。
