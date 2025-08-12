"""
Doc2LaTeX 文档转换工具包

这个包提供了将Word文档转换为LaTeX格式的功能，包括：
- 文档预处理和重命名
- 内容提取和结构化
- LaTeX代码生成
- 图片和格式处理
"""

__version__ = "0.1.0"
__author__ = "Doc2LaTeX Team"

from .main import main

__all__ = ["main"]