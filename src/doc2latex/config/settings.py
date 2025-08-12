"""
项目配置设置

包含所有项目的配置参数和常量定义
"""

import os
import json
from pathlib import Path

# 获取项目根目录 (src layout: src/doc2latex/config/settings.py -> 根目录)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# LaTeX 格式配置
BOLD_COLOR = "blue"  # 粗体颜色
L_TITLE_COLOR = "blue-deep"  # 小标题颜色
LL_TITLE_COLOR = "blue"  # 小小标题颜色
FONT_SIZE = 12  # 字体大小(pt)
PICTURE_POSITION = "htbp"  # 图片位置
PICTURE_WIDTH = "10cm"  # 图片宽度

# 从配置文件加载模块设置
def load_module_config():
    """加载模块配置"""
    config_file = Path(__file__).parent / "modules.json"
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('modules', {}), config.get('modules_traditional', {})
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果配置文件不存在或格式错误，使用默认配置
        default_modules = {
            "名词解释": "green",
            "操作步骤": "green", 
            "实用建议": "orange",
            "编者的话": "red",
            "就医建议": "red"
        }
        default_traditional = {
            "名詞解釋": "green",
            "操作步驟": "green",
            "實用建議": "orange", 
            "編者的話": "red",
            "就醫建議": "red"
        }
        return default_modules, default_traditional

# 模块配置
BOX_DICT, BOX_DICT_TRADITIONAL = load_module_config()

# 列表名称配置
UNORDERED_LIST_NAME = ["无序", "无序列表", "无序列"]
ORDERED_LIST_NAME = ["有序", "有序列表", "有序列"]

# 繁体版列表名称配置
UNORDERED_LIST_NAME_TRADITIONAL = ["無序", "無序列表", "無序列"]
ORDERED_LIST_NAME_TRADITIONAL = ["有序", "有序列表", "有序列"]

# 术语统一配置
TERM_DICT = {
    "劳动派遣": "劳务派遣"
}

# 手册配置
HANDBOOKS = {
    "锻炼手册": {
        "name": "锻炼手册",
        "name_en": "exercise_manual",
        "chapters": list(range(6, 12)),  # 第6-11章
        "description": "身体锻炼、康复训练、运动指导"
    },
    "急救手册": {
        "name": "急救手册", 
        "name_en": "first_aid_manual",
        "chapters": list(range(1, 6)),   # 第1-5章
        "description": "急救知识、紧急处理、医疗指导"
    },
    "食物手册": {
        "name": "食物手册",
        "name_en": "food_manual", 
        "chapters": list(range(12, 15)), # 第12-14章
        "description": "营养知识、饮食建议、健康饮食"
    }
}

# 路径配置
PATHS = {
    "raw_document": PROJECT_ROOT / "data" / "input" / "raw_document",
    "document": PROJECT_ROOT / "data" / "input" / "document", 
    "input_base": PROJECT_ROOT / "data" / "input",
    "image": PROJECT_ROOT / "data" / "assets" / "image",
    "figure": PROJECT_ROOT / "data" / "assets" / "figure",
    "latex_output": PROJECT_ROOT / "latex_output",
    "tex_output": PROJECT_ROOT / "latex_output" / "tex",
    "build_output": PROJECT_ROOT / "latex_output" / "build",
    "pdf_output": PROJECT_ROOT / "latex_output" / "pdf",
    "src": PROJECT_ROOT / "src",
    "templates": PROJECT_ROOT / "data" / "templates"
}

# 确保路径存在
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)