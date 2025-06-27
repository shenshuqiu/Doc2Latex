"""
文件处理工具函数

提供文件路径处理、文件转换等功能。
"""

import os
import shutil
import re
import docx
from pathlib import Path
from typing import List, Optional, Dict, Any
from collections import OrderedDict
try:
    import win32com.client
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from ..config.settings import PATHS


def save_docx_to_dict(docx_file_path: str, document_dict: Dict[str, Any]) -> None:
    """
    将docx文档的内容保存在字典里
    
    Args:
        docx_file_path: 传入的docx文件的路径
        document_dict: 保存内容的字典
    """
    # 通过docx文档路径创建Document类
    document = docx.Document(docx_file_path)

    # 通过路径获得文档的序号：
    # docx_file_path = "document/7-2-3.docx" -> serial = "7-2-3"
    filename = os.path.basename(docx_file_path)
    serial = os.path.splitext(filename)[0]

    # 在document_dict中创建一个字典，键为serial
    document_dict[serial] = OrderedDict()

    # 文档的序号
    document_dict[serial]["serial"] = serial

    # 文档各序号的意义：章数、节数、小节数
    document_dict[serial]["chapter"], document_dict[serial]["section"], document_dict[serial]["subsection"] = map(int, serial.split("-"))

    # 将docx文件中的内容分段落地记录在数组中
    para_list = []
    for para in document.paragraphs:
        # 从网页转换为Word的文档的回车会转换为<w:cr/>，需要手动将\n改成回车
        if "\n" in para.text:
            para_list.extend(para.text.split("\n"))
        else:
            para_list.append(para.text)

    # 筛除空白文档
    assert len(para_list) >= 1, f"{serial}为空白文档"

    # 文档的名字：第一段内容
    document_dict[serial]["name"] = para_list[0]

    # 文档无内容
    if len(para_list) == 1 or len(para_list) == 2:
        document_dict[serial]["text"] = ""
        return
    else:
        document_dict[serial]["text"] = [x for x in para_list[2:] if x != ""]


def image_is_existed(image_name: str, image_path: str = None) -> bool:
    """
    检查图片文件是否存在
    
    Args:
        image_name: 图片名称（不包含扩展名）
        image_path: 图片目录路径，默认使用配置中的路径
        
    Returns:
        图片是否存在
    """
    if image_path is None:
        image_path = str(PATHS["image"])
    
    image_type_list = ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG"]
    for image_type in image_type_list:
        if os.path.exists(os.path.join(image_path, f"{image_name}.{image_type}")):
            return True
    return False


def get_image_filename_with_extension(image_name: str, image_path: str = None) -> str:
    """
    获取带扩展名的完整图片文件名
    
    Args:
        image_name: 图片名称（不包含扩展名）
        image_path: 图片目录路径，默认使用配置中的路径
        
    Returns:
        带扩展名的图片文件名，如果不存在则返回原名称
    """
    if image_path is None:
        image_path = str(PATHS["image"])
    
    image_type_list = ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG"]
    for image_type in image_type_list:
        full_path = os.path.join(image_path, f"{image_name}.{image_type}")
        if os.path.exists(full_path):
            return f"{image_name}.{image_type}"
    return image_name  # 如果找不到，返回原名称


def get_file_list(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    获取指定目录下的文件列表
    
    Args:
        directory: 目录路径
        extensions: 文件扩展名列表，如 ['.docx', '.doc']
        
    Returns:
        符合条件的文件名列表
    """
    if not os.path.exists(directory):
        return []
    
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.startswith("~"):  # 排除临时文件
                if extensions is None:
                    file_list.append(file)
                else:
                    for ext in extensions:
                        if file.lower().endswith(ext.lower()):
                            file_list.append(file)
                            break
    return file_list


def sort_by_serial(file_list: List[str]) -> List[str]:
    """
    根据文件名中的序号对文件列表进行排序
    
    Args:
        file_list: 文件名列表
        
    Returns:
        排序后的文件名列表
    """
    def serial_compare(serial: str) -> float:
        """
        从文件名中提取序号用于排序
        
        Args:
            serial: 文件名
            
        Returns:
            用于排序的数值
        """
        # 提取文件名中的序号部分（不包括扩展名）
        name_without_ext = os.path.splitext(serial)[0]
        try:
            x, y, z = map(float, name_without_ext.split("-"))
            return x * 10000 + y * 100 + z
        except (ValueError, IndexError):
            return 0
    
    return sorted(file_list, key=serial_compare)


def clean_directory(directory: str) -> None:
    """
    清空指定目录中的所有文件
    
    Args:
        directory: 要清空的目录路径
    """
    if not os.path.exists(directory):
        return
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'无法删除 {file_path}。原因: {e}')