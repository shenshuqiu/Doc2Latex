"""
Doc2LaTeX 主程序

提供命令行接口和主要功能入口
"""

import argparse
import sys
from pathlib import Path

from .core.document_processor import DocumentProcessor
from .core.latex_generator import LaTeXGenerator
from .core.latex_generator_traditional import LaTeXGeneratorTraditional
from .config.settings import PATHS


def process_documents():
    """
    处理文档的主流程
    """
    print("=== Doc2LaTeX 文档处理器 ===")
    
    # 创建文档处理器
    processor = DocumentProcessor()
    
    try:
        # 执行完整的文档处理流程
        processor.process_all_documents()
        
        return processor.get_document_dict()
        
    except Exception as e:
        print(f"文档处理失败: {e}")
        sys.exit(1)


def generate_latex(document_dict=None, traditional=False):
    """
    生成LaTeX文档的主流程
    
    Args:
        document_dict: 文档字典，如果为None则先处理文档
        traditional: 是否使用繁体版
    """
    version_name = "繁體版" if traditional else "简体版"
    print(f"=== Doc2LaTeX LaTeX生成器 ({version_name}) ===")
    
    # 如果没有提供文档字典，先处理文档
    if document_dict is None:
        processor = DocumentProcessor()
        processor.load_all_documents()
        document_dict = processor.get_document_dict()
    
    # 创建LaTeX生成器
    if traditional:
        generator = LaTeXGeneratorTraditional(document_dict)
    else:
        generator = LaTeXGenerator(document_dict)
    
    try:
        # 执行完整的LaTeX生成流程
        pdf_path = generator.generate_full_latex()
        
        if pdf_path:
            print(f"LaTeX处理完成！PDF文件已生成: {pdf_path}")
        else:
            print("LaTeX处理失败！")
            sys.exit(1)
            
    except Exception as e:
        print(f"LaTeX生成失败: {e}")
        sys.exit(1)


def full_process(traditional=False):
    """
    完整的处理流程：文档处理 + LaTeX生成
    
    Args:
        traditional: 是否使用繁体版
    """
    version_name = "繁體版" if traditional else "简体版"
    print(f"=== Doc2LaTeX 完整处理流程 ({version_name}) ===")
    
    # 第一步：处理文档
    document_dict = process_documents()
    
    print("\n" + "="*50 + "\n")
    
    # 第二步：生成LaTeX
    generate_latex(document_dict, traditional)


def main():
    """
    主程序入口
    """
    parser = argparse.ArgumentParser(
        description="Doc2LaTeX - 将Word文档转换为LaTeX格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                    # 执行完整流程（文档处理 + LaTeX生成）
  %(prog)s --process-only     # 仅处理文档
  %(prog)s --latex-only       # 仅生成LaTeX（需要已处理的文档）
  
目录结构:
  data/input/raw_document/    # 原始Word文档
  data/input/document/        # 处理后的文档
  data/assets/image/          # 图片资源
  latex_output/tex/           # 生成的LaTeX文件
  latex_output/pdf/           # 最终PDF输出
        """
    )
    
    # 添加命令行参数
    parser.add_argument(
        "--process-only",
        action="store_true",
        help="仅执行文档处理流程"
    )
    
    parser.add_argument(
        "--latex-only", 
        action="store_true",
        help="仅执行LaTeX生成流程"
    )
    
    parser.add_argument(
        "--traditional",
        action="store_true",
        help="使用繁体中文版本"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Doc2LaTeX 0.1.0"
    )
    
    args = parser.parse_args()
    
    # 检查必要的目录
    required_dirs = [
        PATHS["raw_document"],
        PATHS["image"]
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not dir_path.exists():
            missing_dirs.append(str(dir_path))
    
    if missing_dirs:
        print("错误：以下必要目录不存在：")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
        print("\n请确保项目目录结构正确。")
        sys.exit(1)
    
    # 根据参数执行相应流程
    try:
        if args.process_only:
            process_documents()
        elif args.latex_only:
            generate_latex(traditional=args.traditional)
        else:
            full_process(traditional=args.traditional)
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()