"""
DOC转DOCX转换器

提供DOC文件转换为DOCX文件的功能
"""

import os
from typing import Optional
try:
    import win32com.client
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def convert_doc_to_docx(doc_file_path: str, docx_file_path: str) -> None:
    """
    将doc文件转化为docx文件
    
    Args:
        doc_file_path: 传入的doc文件的路径
        docx_file_path: 保存的docx文件的路径
        
    Raises:
        ImportError: 当win32com.client不可用时（非Windows系统）
        FileNotFoundError: 当输入文件不存在时
    """
    if not WIN32_AVAILABLE:
        raise ImportError("win32com.client不可用。doc转docx功能仅在Windows系统上可用")
    
    if not os.path.exists(doc_file_path):
        raise FileNotFoundError(f"文件不存在: {doc_file_path}")
    
    # 获取当前工作目录
    cwd = os.getcwd()
    
    # 将doc文件路径和docx文件路径转换为绝对路径
    abs_doc_file_path = os.path.join(cwd, doc_file_path)
    abs_docx_file_path = os.path.join(cwd, docx_file_path)
    
    # 打开Word应用程序
    word = win32com.client.Dispatch('Word.Application')
    
    try:
        # 打开doc文件
        doc = word.documents.Open(abs_doc_file_path)
        
        # 将doc文件另存为docx文件
        doc.SaveAs(abs_docx_file_path, FileFormat=16)
        
        # 关闭doc文件
        doc.Close()
    finally:
        # 关闭Word应用程序
        word.Quit()

    # 删除doc文件
    os.remove(abs_doc_file_path)