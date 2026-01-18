# Ctrip Car Rental Automation (携程租车自动化脚本)

这是一个基于 `uiautomator2` 的 Android UI 自动化项目，专门用于携程 App (Ctrip) 的租车业务流程自动化。

它采用了**动态 XML 分析**与**智能筛选策略**，能够自动适应不同城市、不同机型的 UI 差异，无需针对每个城市维护静态配置文件。

## 🚀 核心功能

*   **跨城市兼容**：利用 `DynamicXmlLocator` 实时分析页面结构，自动适配不同城市的 UI 布局。
*   **智能筛选器**：`SmartFilter` 支持正则匹配 (`resourceIdMatches`)，自动处理长列表滚动、折叠区域展开与回溯扫描。

## 🛠 环境要求

*   **Python**: 3.8+ (建议 3.10)
*   **OS**: macOS / Windows / Linux
*   **Android Device**: 真机或模拟器 (需开启 USB 调试)

## 📦 依赖安装

建议使用虚拟环境运行本项目：

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt
```

### 核心依赖库说明

| 库名称 | 推荐版本 | 用途 |
| :--- | :--- | :--- |
| `uiautomator2` | >= 2.16.0 | Android 自动化核心驱动 |
| `lxml` | >= 4.9.0 | 高效 XML 解析 (用于页面结构分析) |

## 🏃‍♂️ 快速开始

1.  **连接设备**：
    确保手机已通过 USB 连接电脑，并开启 `USB 调试`。
    ```bash
    adb devices
    ```

2.  **初始化 uiautomator2** (首次运行需执行)：
    ```bash
    python3 -m uiautomator2 init
    ```

3.  **运行脚本**：
    ```bash
    python3 main.py
    ```

## 📂 项目结构

*   `main.py`: **主入口**，负责编排整个自动化流程 (选城市 -> 选日期 -> 筛选 -> 下单)。
*   `smart_filter.py`: **智能筛选器**，核心模块。包含正则匹配、自动滚动、自动展开/回溯逻辑。
*   `dynamic_xml_locator.py`: **动态定位器**，核心模块。负责实时解析 XML 树，智能寻找可点击元素。
*   `select_city.py`: 城市选择逻辑 (支持拼音输入)。
*   `select_time.py`: 日期选择逻辑 (坐标计算)。

## ⚠️ 注意事项

*   **App 版本**：脚本基于携程 Android Debug 版开发 (包名 `ctrip.android.view.debug`)。如在正式版运行，需在 `main.py` 中修改 `PACKAGE_NAME` 为 `ctrip.android.view`。
*   **输入法**：脚本会使用 ADB 键盘输入英文，建议安装 `ADB Keyboard` 以获得最佳体验。
*   **OCR 初始化**：首次运行 `PaddleOCR` 会自动下载模型文件（约 15MB），请保持网络畅通。

## 🤝 贡献与维护

如果你发现某个新城市的 UI 结构无法识别，请提交 Issue 并附上 `dump_hierarchy` 生成的 XML 文件。
