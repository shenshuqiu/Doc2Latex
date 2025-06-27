"""
手册处理器

负责处理多个手册的文档结构，支持按手册分别生成LaTeX。
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from collections import OrderedDict

from .document_processor import DocumentProcessor
from ..config.settings import HANDBOOKS, PATHS
from ..utils.file_utils import get_file_list
from ..utils.logger import get_logger


class HandbookProcessor:
    """手册处理器类，用于管理多个手册的处理流程"""
    
    def __init__(self):
        """初始化手册处理器"""
        self.input_base = PATHS["input_base"]
        self.document_dir = PATHS["document"]
        self.raw_document_dir = PATHS["raw_document"]
        self.handbooks = {}
        self.processors = {}
        self.logger = get_logger()
        self.current_file_mapping = {}  # 当前手册的文件映射关系
    
    def discover_handbooks(self) -> Dict[str, Dict]:
        """
        发现并验证输入目录中的手册
        
        Returns:
            Dict: 发现的手册信息
        """
        discovered = {}
        
        for handbook_name, config in HANDBOOKS.items():
            handbook_path = self.input_base / handbook_name
            
            if handbook_path.exists() and handbook_path.is_dir():
                # 检查文件
                docx_files = list(handbook_path.glob("*.docx"))
                image_files = list(handbook_path.glob("*.jpg")) + \
                             list(handbook_path.glob("*.JPG")) + \
                             list(handbook_path.glob("*.png")) + \
                             list(handbook_path.glob("*.PNG")) + \
                             list(handbook_path.glob("*.jpeg")) + \
                             list(handbook_path.glob("*.JPEG"))
                # 过滤掉封面文件
                image_files = [f for f in image_files if f.name != "cover.pdf"]
                cover_file = handbook_path / "cover.pdf"
                
                discovered[handbook_name] = {
                    "path": handbook_path,
                    "config": config,
                    "docx_files": len(docx_files),
                    "image_files": len(image_files),
                    "has_cover": cover_file.exists(),
                    "docx_list": [f.name for f in docx_files],
                    "image_list": [f.name for f in image_files]
                }
                
                self.logger.log_handbook_discovery(
                    handbook_name, len(docx_files), len(image_files), cover_file.exists()
                )
        
        self.handbooks = discovered
        return discovered
    
    def prepare_handbook_processing(self, handbook_name: str) -> bool:
        """
        为指定手册准备处理环境
        
        Args:
            handbook_name: 手册名称
            
        Returns:
            bool: 准备是否成功
        """
        if handbook_name not in self.handbooks:
            print(f"错误: 未找到手册 {handbook_name}")
            return False
        
        handbook_info = self.handbooks[handbook_name]
        handbook_path = handbook_info["path"]
        
        # 清理并准备目录
        if self.raw_document_dir.exists():
            shutil.rmtree(self.raw_document_dir)
        if self.document_dir.exists():
            shutil.rmtree(self.document_dir)
            
        self.raw_document_dir.mkdir(parents=True, exist_ok=True)
        self.document_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制DocX文件到raw_document目录，并重新映射章节编号
        docx_files = list(handbook_path.glob("*.docx"))
        chapter_mapping = self._create_chapter_mapping(docx_files)
        file_mapping = {}  # 存储文件映射关系
        
        for docx_file in docx_files:
            if docx_file.name != "cover.pdf":  # 跳过封面文件
                # 重新映射文件名
                new_filename = self._remap_filename(docx_file.name, chapter_mapping)
                dest_file = self.raw_document_dir / new_filename
                shutil.copy2(docx_file, dest_file)
                # 存储映射关系
                file_mapping[docx_file.name] = new_filename
        
        # 存储文件映射关系供后续使用
        self.current_file_mapping = file_mapping
        
        # 准备图片目录（收集所有手册的图片）
        self._prepare_all_images()
        
        image_count = len(list(PATHS["image"].glob("*")))
        self.logger.log_processing_summary(handbook_name, len(docx_files), image_count)
        
        return True
    
    def process_handbook(self, handbook_name: str) -> Optional[DocumentProcessor]:
        """
        处理指定手册
        
        Args:
            handbook_name: 手册名称
            
        Returns:
            DocumentProcessor: 处理器实例，失败返回None
        """
        if not self.prepare_handbook_processing(handbook_name):
            return None
        
        # 为这个手册创建专用日志
        handbook_logger = get_logger(handbook_name)
        handbook_logger.section(f"开始处理手册: {handbook_name}")
        
        # 创建文档处理器
        processor = DocumentProcessor()
        
        # 传递文件映射关系
        processor.file_mapping = self.current_file_mapping
        
        try:
            # 执行文档处理流程
            processor.process_all_documents()
            
            # 保存处理器
            self.processors[handbook_name] = processor
            
            handbook_logger.success(f"手册 {handbook_name} 处理完成!")
            return processor
            
        except Exception as e:
            handbook_logger.error(f"处理手册 {handbook_name} 时出错: {e}")
            return None
    
    def process_all_handbooks(self) -> Dict[str, DocumentProcessor]:
        """
        处理所有发现的手册
        
        Returns:
            Dict: 手册名称到处理器的映射
        """
        self.discover_handbooks()
        
        if not self.handbooks:
            print("警告: 未发现任何手册")
            return {}
        
        results = {}
        
        for handbook_name in self.handbooks.keys():
            processor = self.process_handbook(handbook_name)
            if processor:
                results[handbook_name] = processor
            
            print("\n" + "="*50 + "\n")
        
        return results
    
    def get_handbook_info(self, handbook_name: str) -> Optional[Dict]:
        """获取指定手册的信息"""
        return self.handbooks.get(handbook_name)
    
    def list_handbooks(self) -> List[str]:
        """列出所有可用的手册"""
        return list(self.handbooks.keys())
    
    def validate_handbook_structure(self, handbook_name: str) -> Dict[str, bool]:
        """
        验证手册结构的完整性
        
        Args:
            handbook_name: 手册名称
            
        Returns:
            Dict: 验证结果
        """
        if handbook_name not in self.handbooks:
            return {"exists": False}
        
        handbook_info = self.handbooks[handbook_name]
        
        validation = {
            "exists": True,
            "has_docx": handbook_info["docx_files"] > 0,
            "has_images": handbook_info["image_files"] > 0,
            "has_cover": handbook_info["has_cover"],
            "docx_count": handbook_info["docx_files"],
            "image_count": handbook_info["image_files"]
        }
        
        # 检查DocX文件命名格式
        valid_names = 0
        invalid_names = []
        
        for docx_name in handbook_info["docx_list"]:
            if self._is_valid_docx_name(docx_name):
                valid_names += 1
            else:
                invalid_names.append(docx_name)
        
        validation["valid_docx_names"] = valid_names == handbook_info["docx_files"]
        validation["invalid_names"] = invalid_names
        
        return validation
    
    def _is_valid_docx_name(self, filename: str) -> bool:
        """检查DocX文件名格式是否正确"""
        if not filename.endswith('.docx'):
            return False
        
        basename = filename[:-5]  # 移除.docx
        parts = basename.split('-')
        
        if len(parts) != 3:
            return False
        
        try:
            # 检查是否都是数字
            for part in parts:
                int(part)
            return True
        except ValueError:
            return False
    
    def generate_handbook_report(self) -> str:
        """生成手册处理报告"""
        if not self.handbooks:
            return "未发现任何手册"
        
        report = ["=== 手册处理报告 ===\n"]
        
        for handbook_name, info in self.handbooks.items():
            report.append(f"手册: {handbook_name}")
            report.append(f"  描述: {info['config']['description']}")
            report.append(f"  章节范围: {info['config']['chapters']}")
            report.append(f"  DocX文件: {info['docx_files']}个")
            report.append(f"  图片文件: {info['image_files']}个")
            report.append(f"  封面文件: {'✓' if info['has_cover'] else '✗'}")
            
            # 验证结果
            validation = self.validate_handbook_structure(handbook_name)
            if not validation["valid_docx_names"]:
                report.append(f"  警告: 发现无效文件名: {validation['invalid_names']}")
            
            report.append("")
        
        return "\n".join(report)
    
    def _create_chapter_mapping(self, docx_files: List[Path]) -> Dict[int, int]:
        """
        创建章节映射表，将原始章节号映射到从1开始的连续章节号
        
        Args:
            docx_files: DocX文件列表
            
        Returns:
            Dict: 原始章节号到新章节号的映射
        """
        original_chapters = set()
        
        # 收集所有原始章节号
        for docx_file in docx_files:
            filename = docx_file.name
            if filename.endswith('.docx'):
                basename = filename[:-5]
                parts = basename.split('-')
                if len(parts) == 3:
                    try:
                        original_chapter = int(parts[0])
                        original_chapters.add(original_chapter)
                    except ValueError:
                        continue
        
        # 创建映射：原始章节号 -> 新章节号（从1开始）
        sorted_chapters = sorted(original_chapters)
        chapter_mapping = {}
        
        for new_chapter, original_chapter in enumerate(sorted_chapters, 1):
            chapter_mapping[original_chapter] = new_chapter
        
        self.logger.log_chapter_mapping(chapter_mapping)
        return chapter_mapping
    
    def _remap_filename(self, filename: str, chapter_mapping: Dict[int, int]) -> str:
        """
        根据章节映射重新映射文件名
        
        Args:
            filename: 原始文件名
            chapter_mapping: 章节映射表
            
        Returns:
            str: 新的文件名
        """
        if not filename.endswith('.docx'):
            return filename
        
        basename = filename[:-5]
        parts = basename.split('-')
        
        if len(parts) != 3:
            return filename
        
        try:
            original_chapter = int(parts[0])
            section = int(parts[1])
            subsection = int(parts[2])
            
            # 映射章节号
            if original_chapter in chapter_mapping:
                new_chapter = chapter_mapping[original_chapter]
                new_filename = f"{new_chapter}-{section}-{subsection}.docx"
                self.logger.log_file_remapping(filename, new_filename)
                return new_filename
            else:
                self.logger.warning(f"章节 {original_chapter} 未在映射表中找到，保持原文件名: {filename}")
                return filename
                
        except ValueError:
            self.logger.warning(f"无法解析文件名格式: {filename}")
            return filename
    
    def _prepare_all_images(self):
        """
        收集所有手册文件夹中的图片，统一存放到assets/image目录
        处理重名问题
        """
        image_dir = PATHS["image"]
        
        # 清理并创建图片目录
        if image_dir.exists():
            shutil.rmtree(image_dir)
        image_dir.mkdir(parents=True, exist_ok=True)
        
        image_extensions = [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"]
        copied_images = {}  # 用于跟踪已复制的图片和重名处理
        
        self.logger.debug("开始收集所有手册的图片...")
        
        # 遍历所有手册文件夹
        for handbook_name in HANDBOOKS.keys():
            handbook_path = self.input_base / handbook_name
            
            if not handbook_path.exists():
                continue
                
            self.logger.debug(f"收集手册 {handbook_name} 的图片...")
            
            # 收集该手册的所有图片
            for ext in image_extensions:
                for img_file in handbook_path.glob(f"*{ext}"):
                    original_name = img_file.name
                    base_name = img_file.stem
                    file_ext = img_file.suffix
                    
                    # 处理重名问题
                    if original_name in copied_images:
                        # 检查文件是否相同
                        existing_file = copied_images[original_name]
                        if img_file.stat().st_size == existing_file.stat().st_size:
                            self.logger.debug(f"跳过重复图片: {original_name}")
                            continue
                        else:
                            # 文件名相同但内容不同，需要重命名
                            counter = 1
                            while True:
                                new_name = f"{base_name}_{handbook_name}_{counter}{file_ext}"
                                if new_name not in copied_images:
                                    break
                                counter += 1
                            
                            dest_file = image_dir / new_name
                            shutil.copy2(img_file, dest_file)
                            copied_images[new_name] = img_file
                            self.logger.debug(f"重命名复制图片: {original_name} -> {new_name}")
                    else:
                        # 没有重名，直接复制
                        dest_file = image_dir / original_name
                        shutil.copy2(img_file, dest_file)
                        copied_images[original_name] = img_file
                        self.logger.debug(f"复制图片: {original_name}")
        
        total_images = len(copied_images)
        self.logger.info(f"图片收集完成，共收集 {total_images} 个图片文件")