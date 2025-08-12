"""
日志管理模块

提供统一的日志记录功能，控制台显示简洁信息，详细信息记录到文件。
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..config.settings import PATHS


class Doc2LaTeXLogger:
    """Doc2LaTeX专用日志记录器"""
    
    def __init__(self, handbook_name: Optional[str] = None):
        """
        初始化日志记录器
        
        Args:
            handbook_name: 手册名称，用于创建专用日志文件
        """
        self.handbook_name = handbook_name
        self.errors = []
        self.warnings = []
        
        # 创建日志目录
        self.log_dir = PATHS["input_base"] / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 设置日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if handbook_name:
            self.log_file = self.log_dir / f"{handbook_name}_{timestamp}.log"
        else:
            self.log_file = self.log_dir / f"doc2latex_{timestamp}.log"
        
        # 配置日志
        self._setup_logger()
    
    def _setup_logger(self):
        """配置日志记录器"""
        # 创建日志记录器
        self.logger = logging.getLogger(f"doc2latex_{self.handbook_name or 'main'}")
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 文件处理器 - 记录所有详细信息
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 控制台处理器 - 只显示重要信息
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, console: bool = False):
        """记录信息"""
        self.logger.info(message)
        if console:
            print(f"ℹ️  {message}")
    
    def debug(self, message: str):
        """记录调试信息（仅文件）"""
        self.logger.debug(message)
    
    def warning(self, message: str, console: bool = True):
        """记录警告"""
        self.warnings.append(message)
        self.logger.warning(message)
        if console:
            print(f"⚠️  {message}")
    
    def error(self, message: str, console: bool = True):
        """记录错误"""
        self.errors.append(message)
        self.logger.error(message)
        if console:
            print(f"❌ {message}")
    
    def success(self, message: str, console: bool = True):
        """记录成功信息"""
        self.logger.info(f"SUCCESS: {message}")
        if console:
            print(f"✅ {message}")
    
    def section(self, title: str, console: bool = True):
        """开始新的处理阶段"""
        separator = "=" * 50
        self.logger.info(f"\n{separator}\n{title}\n{separator}")
        if console:
            print(f"\n=== {title} ===")
    
    def log_chapter_mapping(self, mapping: dict):
        """记录章节映射信息"""
        self.debug("章节重新映射：")
        for original, new in mapping.items():
            self.debug(f"  第{original}章 -> 第{new}章")
    
    def log_file_remapping(self, original: str, new: str):
        """记录文件重新映射"""
        self.debug(f"文件映射: {original} -> {new}")
    
    def log_handbook_discovery(self, handbook_name: str, docx_count: int, image_count: int, has_cover: bool):
        """记录手册发现信息"""
        self.debug(f"发现手册: {handbook_name}")
        self.debug(f"  - DocX文件: {docx_count}个")
        self.debug(f"  - 图片文件: {image_count}个")
        self.debug(f"  - 封面文件: {'✓' if has_cover else '✗'}")
    
    def log_processing_summary(self, handbook_name: str, docx_copied: int, images_copied: int):
        """记录处理摘要"""
        self.info(f"已为手册 {handbook_name} 准备处理环境", console=True)
        self.debug(f"  - 复制了 {docx_copied} 个DocX文件")
        self.debug(f"  - 复制了 {images_copied} 个图片文件")
    
    def report_syntax_error(self, serial: str, syntax: str, suggestions: List[str] = None):
        """报告语法错误"""
        error_msg = f"在文档 {serial} 中发现未支持的语法: 【{syntax}】"
        self.error(error_msg)
        
        if suggestions:
            self.info("可能的解决方案:")
            for i, suggestion in enumerate(suggestions, 1):
                self.info(f"  {i}. {suggestion}")
    
    def get_summary(self) -> dict:
        """获取处理摘要"""
        return {
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "error_list": self.errors.copy(),
            "warning_list": self.warnings.copy(),
            "log_file": str(self.log_file)
        }
    
    def print_summary(self):
        """打印处理摘要"""
        summary = self.get_summary()
        
        if summary["errors"] > 0:
            self.error(f"发现 {summary['errors']} 个错误，请检查后重试")
            print("\n主要错误:")
            for error in summary["error_list"][:3]:  # 只显示前3个错误
                print(f"  • {error}")
            if len(summary["error_list"]) > 3:
                print(f"  ... 还有 {len(summary['error_list']) - 3} 个错误")
        
        if summary["warnings"] > 0:
            print(f"\n⚠️  发现 {summary['warnings']} 个警告")
        
        if summary["errors"] == 0:
            self.success("处理完成！")
        
        print(f"\n📄 详细日志已保存到: {summary['log_file']}")


# 全局日志实例
_current_logger: Optional[Doc2LaTeXLogger] = None


def get_logger(handbook_name: Optional[str] = None) -> Doc2LaTeXLogger:
    """获取当前日志实例"""
    global _current_logger
    if _current_logger is None or (handbook_name and _current_logger.handbook_name != handbook_name):
        _current_logger = Doc2LaTeXLogger(handbook_name)
    return _current_logger


def set_logger(logger: Doc2LaTeXLogger):
    """设置当前日志实例"""
    global _current_logger
    _current_logger = logger