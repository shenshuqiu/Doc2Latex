# Doc2LaTeX 项目架构说明

## 项目结构 (Src Layout)

Doc2LaTeX 项目采用标准的 src layout 布局，项目结构如下：

```
/Users/mac/Public/09-Code/091-Python/0911-Doc2Latex/
├── src/                           # 源代码目录
│   ├── doc2latex/                 # 主包
│   │   ├── __init__.py
│   │   ├── main.py               # 主程序入口
│   │   ├── config/               # 配置模块
│   │   │   ├── __init__.py
│   │   │   ├── settings.py       # 项目设置
│   │   │   └── modules.json      # 模块配置文件
│   │   ├── core/                 # 核心功能模块
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py       # 文档处理器
│   │   │   ├── handbook_processor.py       # 手册处理器
│   │   │   ├── latex_generator.py          # LaTeX生成器（简体）
│   │   │   ├── latex_generator_traditional.py  # LaTeX生成器（繁体）
│   │   │   └── tree_manager.py             # 树状结构管理器
│   │   └── utils/                # 工具模块
│   │       ├── __init__.py
│   │       ├── doc_converter.py            # 文档转换工具
│   │       ├── file_utils.py               # 文件操作工具
│   │       ├── logger.py                   # 日志工具
│   │       ├── text_utils.py               # 文本处理工具（简体）
│   │       └── text_utils_traditional.py   # 文本处理工具（繁体）
│   └── elegantbook.cls           # LaTeX 文档类
├── tests/                        # 测试目录
│   └── test_module_config.py     # 模块配置测试
├── data/                         # 数据目录
│   ├── assets/                   # 资源文件
│   │   ├── figure/              # 图形文件
│   │   └── image/               # 图片文件
│   ├── input/                   # 输入文件
│   │   ├── document/            # 处理后的文档
│   │   ├── raw_document/        # 原始文档
│   │   ├── logs/                # 日志文件
│   │   ├── 锻炼手册/             # 锻炼手册项目
│   │   ├── 急救手册/             # 急救手册项目
│   │   └── 食物手册/             # 食物手册项目
│   └── templates/               # 模板文件
├── latex_output/                # LaTeX 输出目录
│   ├── tex/                     # 生成的 .tex 文件
│   ├── build/                   # 编译临时文件
│   └── pdf/                     # 最终 PDF 输出
├── archive/                     # 归档文件
├── pyproject.toml              # 项目配置文件
├── README.md                   # 项目说明
├── INPUT_FORMAT.md             # 输入格式说明
├── 语法规则书.md                # 语法规则文档
└── uv.lock                     # 依赖锁定文件
```

## Src Layout 的优势

1. **清晰的代码组织**：源代码与其他文件（测试、配置、数据）明确分离
2. **避免导入冲突**：防止测试时意外导入项目根目录下的模块
3. **标准化结构**：符合 Python 包装和分发的最佳实践
4. **工具支持**：大多数现代 Python 工具都支持 src layout

## 主要模块说明

### Core 模块

- **document_processor.py**: 负责处理Word文档，提取内容和结构
- **handbook_processor.py**: 管理多个手册项目的处理流程
- **latex_generator.py**: 生成简体中文的LaTeX文档
- **latex_generator_traditional.py**: 生成繁体中文的LaTeX文档
- **tree_manager.py**: 管理文档的树状结构

### Utils 模块

- **text_utils.py**: 简体中文文本处理，包括语法解析和特殊字符处理
- **text_utils_traditional.py**: 繁体中文文本处理
- **file_utils.py**: 文件操作工具，包括图片处理和文件检查
- **logger.py**: 统一的日志管理系统
- **doc_converter.py**: 文档格式转换工具

### Config 模块

- **settings.py**: 项目全局设置，包括路径配置和格式设置
- **modules.json**: 可配置的模块颜色系统

## 新增功能

### 1. 脚注语法支持
- 简体版：`【脚注：内容】` 或 `【脚注:内容】`
- 繁体版：`【腳註：內容】` 或 `【腳註:內容】`
- 自动生成 LaTeX 脚注：`\footnote{内容}`

### 2. 灵活的项目输入
- 自动发现 `data/input/` 下的所有文件夹作为项目
- 智能跳过系统文件夹（document、raw_document、logs等）
- 为新项目自动生成默认配置
- 完全向下兼容原有的手册系统

### 3. 智能封面处理
- 自动检查封面文件存在性
- 当封面缺失时，自动回退到默认封面或生成简单标题页
- 提供友好的警告信息

## 使用方法

```bash
# 安装项目（开发模式）
uv pip install -e .

# 列出所有可用项目
uv run doc2latex --list-handbooks

# 处理特定项目
uv run doc2latex --handbook "项目名称"

# 处理所有项目
uv run doc2latex

# 生成繁体版本
uv run doc2latex --traditional

# 仅处理文档（不生成LaTeX）
uv run doc2latex --process-only

# 仅生成LaTeX（需要已处理的文档）
uv run doc2latex --latex-only
```

## 开发工具配置

项目配置了以下开发工具，都已适配 src layout：

- **Black**: 代码格式化，配置为只处理 `src/` 目录
- **isort**: 导入排序，设置了 `src_paths = ["src", "tests"]`
- **mypy**: 类型检查，配置了 `mypy_path = "src"`
- **pytest**: 单元测试，配置了覆盖率检查路径 `--cov=src/doc2latex`

## 版本信息

- **版本**: 0.1.0
- **Python**: >= 3.9
- **构建系统**: Hatchling
- **包管理**: uv

## 项目特点

1. **多语言支持**：完整的简繁体中文支持
2. **模块化设计**：清晰的模块划分和职责分离
3. **可配置性**：支持自定义模块颜色和项目配置
4. **错误处理**：完善的错误处理和用户友好的提示
5. **标准化**：符合现代Python项目的最佳实践