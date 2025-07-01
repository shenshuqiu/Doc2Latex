# Doc2LaTeX

一个将Word文档转换为LaTeX格式的Python工具包，支持简体和繁体中文。

## 功能特性

- 📄 **文档处理**: 支持doc/docx文件的读取和处理
- 🏗️ **结构化**: 自动识别文档的章节结构并重新编号
- 🎨 **格式转换**: 将特殊语法转换为LaTeX格式
- 📊 **图片支持**: 自动处理和引用图片，支持简繁体名称匹配
- 🔧 **模块化**: 完全重构的模块化代码结构
- 🌏 **双版本**: 支持简体中文和繁体中文两个版本
- ⚙️ **可配置**: 支持通过配置文件自定义模块颜色和类型

## 安装与使用

### 使用uv（推荐）

```bash
# 安装依赖
uv sync

# 运行完整流程（简体版）
uv run doc2latex

# 运行繁体版
uv run doc2latex --traditional

# 仅处理文档
uv run doc2latex --process-only

# 仅生成LaTeX（繁体版）
uv run doc2latex --latex-only --traditional
```

## 版本特性

### 简体版
- 使用简体中文术语（名词解释、操作步骤等）
- 图片引用使用"图"
- 标准简体中文语法标记

### 繁体版
- 使用繁体中文术语（名詞解釋、操作步驟等）
- 图片引用使用"圖"
- 支持简繁体图片名称混合匹配
- 标签统一使用繁体中文
- 基于OpenCC进行简繁转换

## 项目结构

```
doc2latex/
├── doc2latex/                 # 核心代码包
│   ├── core/                 # 核心模块
│   │   ├── document_processor.py      # 文档处理器
│   │   ├── latex_generator.py         # LaTeX生成器（简体版）
│   │   ├── latex_generator_traditional.py  # LaTeX生成器（繁体版）
│   │   └── tree_manager.py           # 树结构管理
│   ├── utils/                # 工具模块
│   │   ├── file_utils.py             # 文件操作工具
│   │   ├── text_utils.py             # 文本处理工具（简体版）
│   │   ├── text_utils_traditional.py # 文本处理工具（繁体版）
│   │   └── doc_converter.py          # doc转docx转换器
│   └── config/               # 配置模块
│       ├── settings.py              # 主配置文件
│       └── modules.json             # 模块颜色配置文件
├── data/                     # 数据目录（git忽略）
├── latex_output/            # LaTeX编译输出（git忽略）
├── archive/                 # 归档目录（git忽略）
└── tests/                   # 测试文件
```

## 重构说明

本项目完成了从Jupyter Notebook到模块化Python包的重构：

1. **代码组织**: 将原来的.ipynb代码重构为模块化的.py文件
2. **包管理**: 使用uv管理依赖和项目配置
3. **目录结构**: 分离核心代码与数据，创建清晰的目录结构
4. **中文注释**: 所有函数都有详细的中文注释，符合Python代码规范
5. **版本控制**: 原始文件归档，数据目录排除在git外
6. **双语支持**: 实现简体和繁体两个版本

## 归档说明

- 原始的.ipynb文件已移动到`archive/original_notebooks/`
- 其他原始文件已移动到`archive/original_files/`
- 数据目录和归档目录已从git版本控制中排除

## 配置文件说明

### 模块颜色配置

项目支持通过 `doc2latex/config/modules.json` 配置文件自定义模块的颜色和类型：

```json
{
  "description": "模块颜色配置文件",
  "version": "1.0",
  "available_colors": [
    "green",
    "orange", 
    "red"
  ],
  "modules": {
    "名词解释": "green",
    "操作步骤": "green",
    "实用建议": "orange",
    "编者的话": "red",
    "就医建议": "red"
  },
  "modules_traditional": {
    "名詞解釋": "green",
    "操作步驟": "green", 
    "實用建議": "orange",
    "編者的話": "red",
    "就醫建議": "red"
  }
}
```

#### 配置说明

- **available_colors**: 可用的颜色列表，目前支持 `green`、`orange`、`red` 三种颜色
- **modules**: 简体中文模块配置，格式为 `"模块名": "颜色"`
- **modules_traditional**: 繁体中文模块配置，格式同上

#### 使用方法

1. **添加新模块**: 在 `modules` 或 `modules_traditional` 中添加新的键值对
2. **修改颜色**: 将模块对应的颜色值改为三种可用颜色之一
3. **自动生效**: 重新运行程序时会自动加载新配置

#### 错误处理

- 如果配置文件不存在或格式错误，系统会自动使用默认配置
- 系统会验证颜色是否为有效值，无效颜色会导致配置加载失败

#### 测试配置

可以运行以下命令测试配置功能：

```bash
python tests/test_module_config.py
```

该测试脚本会验证：
- 配置文件加载功能
- 错误处理机制
- 动态配置更新
- 繁体中文配置
- 颜色验证
EOF < /dev/null