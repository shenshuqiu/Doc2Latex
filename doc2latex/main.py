"""
Doc2LaTeX 主程序

提供命令行接口和主要功能入口
"""

import argparse
import sys
from pathlib import Path

from .core.document_processor import DocumentProcessor
from .core.handbook_processor import HandbookProcessor
from .core.latex_generator import LaTeXGenerator
from .core.latex_generator_traditional import LaTeXGeneratorTraditional
from .config.settings import PATHS, HANDBOOKS
from .utils.logger import get_logger


def process_documents():
    """
    处理文档的主流程（传统单一文档模式）
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


def process_handbooks(handbook_name=None):
    """
    处理手册的主流程
    
    Args:
        handbook_name: 指定手册名称，None表示处理所有手册
    """
    logger = get_logger()
    logger.section("Doc2LaTeX 手册处理器")
    
    # 创建手册处理器
    handbook_processor = HandbookProcessor()
    
    try:
        # 先发现所有手册
        handbook_processor.discover_handbooks()
        
        if handbook_name:
            # 处理指定手册
            if handbook_name not in handbook_processor.handbooks:
                logger.error(f"未找到手册 '{handbook_name}'")
                available = list(handbook_processor.handbooks.keys())
                logger.info(f"可用手册: {available}")
                sys.exit(1)
            
            processor = handbook_processor.process_handbook(handbook_name)
            if processor:
                return {handbook_name: processor}
            else:
                sys.exit(1)
        else:
            # 处理所有手册
            results = handbook_processor.process_all_handbooks()
            if not results:
                logger.error("未成功处理任何手册")
                sys.exit(1)
            return results
        
    except Exception as e:
        logger.error(f"手册处理失败: {e}")
        sys.exit(1)


def generate_latex(document_dict=None, traditional=False, handbook_name=None, document_processor=None):
    """
    生成LaTeX文档的主流程
    
    Args:
        document_dict: 文档字典，如果为None则先处理文档
        traditional: 是否使用繁体版
        handbook_name: 手册名称，用于生成特定手册的LaTeX
    """
    version_name = "繁體版" if traditional else "简体版"
    handbook_info = f" - {handbook_name}" if handbook_name else ""
    print(f"=== Doc2LaTeX LaTeX生成器 ({version_name}{handbook_info}) ===")
    
    # 如果没有提供文档字典，先处理文档
    if document_dict is None:
        processor = DocumentProcessor()
        processor.load_all_documents()
        document_dict = processor.get_document_dict()
    
    # 创建LaTeX生成器
    if traditional:
        generator = LaTeXGeneratorTraditional(document_dict, document_processor, handbook_name)
    else:
        generator = LaTeXGenerator(document_dict, document_processor, handbook_name)
    
    try:
        # 执行完整的LaTeX生成流程
        pdf_path = generator.generate_full_latex()
        
        if pdf_path:
            print(f"LaTeX处理完成！PDF文件已生成: {pdf_path}")
            return pdf_path
        else:
            print("LaTeX处理失败！")
            sys.exit(1)
            
    except Exception as e:
        print(f"LaTeX生成失败: {e}")
        sys.exit(1)


def generate_handbooks_latex(handbook_processors, traditional=False):
    """
    为多个手册生成LaTeX文档
    
    Args:
        handbook_processors: 手册处理器字典
        traditional: 是否使用繁体版
    """
    results = {}
    
    for handbook_name, processor in handbook_processors.items():
        print(f"\n为手册 '{handbook_name}' 生成LaTeX...")
        
        try:
            document_dict = processor.get_document_dict()
            pdf_path = generate_latex(document_dict, traditional, handbook_name, processor)
            results[handbook_name] = pdf_path
            
        except Exception as e:
            print(f"为手册 '{handbook_name}' 生成LaTeX失败: {e}")
            results[handbook_name] = None
    
    return results


def full_process(traditional=False, handbook_name=None):
    """
    完整的处理流程：文档处理 + LaTeX生成
    
    Args:
        traditional: 是否使用繁体版
        handbook_name: 指定手册名称，None表示处理所有手册
    """
    version_name = "繁體版" if traditional else "简体版"
    mode = "手册模式" if handbook_name or any(Path(PATHS["input_base"] / name).exists() for name in HANDBOOKS.keys()) else "传统模式"
    print(f"=== Doc2LaTeX 完整处理流程 ({version_name} - {mode}) ===")
    
    # 检查是否有手册文件夹
    has_handbooks = any(Path(PATHS["input_base"] / name).exists() for name in HANDBOOKS.keys())
    
    if has_handbooks:
        # 手册模式
        print("检测到手册文件夹，使用手册处理模式")
        
        # 第一步：处理手册
        handbook_processors = process_handbooks(handbook_name)
        
        print("\n" + "="*50 + "\n")
        
        # 第二步：生成LaTeX
        results = generate_handbooks_latex(handbook_processors, traditional)
        
        # 显示结果
        print("\n=== 处理结果 ===")
        for name, pdf_path in results.items():
            status = "✓ 成功" if pdf_path else "✗ 失败"
            print(f"{status} - {name}: {pdf_path or '无输出'}")
            
    else:
        # 传统模式
        print("使用传统处理模式")
        
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
  %(prog)s                           # 执行完整流程（自动检测手册或传统模式）
  %(prog)s --process-only            # 仅处理文档
  %(prog)s --latex-only              # 仅生成LaTeX（需要已处理的文档）
  %(prog)s --handbook "锻炼手册"        # 处理指定手册
  %(prog)s --list-handbooks         # 列出可用手册
  %(prog)s --traditional             # 使用繁体中文版本
  
目录结构:
  传统模式:
    data/input/raw_document/         # 原始Word文档
    data/input/document/             # 处理后的文档
    data/assets/image/               # 图片资源
    
  手册模式:
    data/input/锻炼手册/              # 锻炼手册文件夹
    data/input/急救手册/              # 急救手册文件夹
    data/input/食物手册/              # 食物手册文件夹
    
  输出:
    latex_output/tex/                # 生成的LaTeX文件
    latex_output/pdf/                # 最终PDF输出
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
        "--handbook",
        type=str,
        help="处理指定的手册（锻炼手册、急救手册、食物手册）"
    )
    
    parser.add_argument(
        "--list-handbooks",
        action="store_true",
        help="列出所有可用的手册"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Doc2LaTeX 0.1.0"
    )
    
    args = parser.parse_args()
    
    # 处理列出手册的请求
    if args.list_handbooks:
        handbook_processor = HandbookProcessor()
        handbook_processor.discover_handbooks()
        print(handbook_processor.generate_handbook_report())
        return
    
    # 检查是否有手册文件夹
    has_handbooks = any(Path(PATHS["input_base"] / name).exists() for name in HANDBOOKS.keys())
    
    if not has_handbooks:
        # 传统模式，检查必要目录
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
            print("\n请确保项目目录结构正确，或创建手册文件夹。")
            print("\n手册模式目录结构:")
            for name in HANDBOOKS.keys():
                print(f"  - data/input/{name}/")
            sys.exit(1)
    
    # 根据参数执行相应流程
    try:
        if args.process_only:
            if has_handbooks:
                process_handbooks(args.handbook)
            else:
                process_documents()
        elif args.latex_only:
            generate_latex(traditional=args.traditional)
        else:
            full_process(traditional=args.traditional, handbook_name=args.handbook)
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()