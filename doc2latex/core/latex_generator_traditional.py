"""
繁体版LaTeX生成器

负责将文档转换为LaTeX格式并生成PDF（繁体中文版本）
"""

import os
from collections import OrderedDict
from typing import Dict, Any
from pylatex import Document, Command, Package, NoEscape

from ..config.settings import (
    FONT_SIZE, PATHS
)
from ..utils.text_utils_traditional import (
    special_character_replacement_traditional, 
    syntax_interpreter_traditional,
    check_chinese_square_brackets_pairs
)


class LaTeXGeneratorTraditional:
    """繁体版LaTeX生成器类"""
    
    def __init__(self, document_dict: Dict[str, Any] = None):
        """
        初始化繁体版LaTeX生成器
        
        Args:
            document_dict: 文档字典
        """
        self.document_dict = document_dict or OrderedDict()
        self.latex_doc = None
        
    def set_document_dict(self, document_dict: Dict[str, Any]) -> None:
        """
        设置文档字典
        
        Args:
            document_dict: 文档字典
        """
        self.document_dict = document_dict
    
    def validate_document_brackets(self) -> None:
        """
        验证文档中的中文方括号配对（繁体版）
        """
        for serial, content in self.document_dict.items():
            if content.get("text"):
                for paragraph_num, paragraph in enumerate(content["text"]):
                    if not check_chinese_square_brackets_pairs(paragraph):
                        raise AssertionError(f"方括號未配對: {serial} 第{paragraph_num + 1}段")
    
    def create_latex_document(self) -> None:
        """
        创建LaTeX文档（繁体版）
        """
        # 创建LaTeX文档
        self.latex_doc = Document(
            "main_before_traditional",
            documentclass=str(PATHS["templates"] / "elegantbook.cls"),
            document_options=["lang=cn", "scheme=chinese", f"{FONT_SIZE}pt"]
        )
        
        # 添加包
        packages = [
            "tcolorbox", "color", "pdfpages", "titletoc", "float"
        ]
        for package in packages:
            self.latex_doc.packages.append(Package(package))
        
        # 添加前言设置
        preamble_commands = [
            r"\titlecontents{chapter}[3em]{\bfseries \vspace{7pt}}{\contentslabel{4.5em}}{\hspace*{-1em}}{~\titlerule*[0.6pc]{$.$}~\contentspage}",
            r"\titlecontents{section}[4em]{\vspace{6pt}}{\contentslabel{2.3em}}{\hspace*{-4em}}{~\titlerule*[0.6pc]{$.$}~\contentspage}",
            r"\titlecontents{subsection}[6em]{\vspace{5pt}}{\contentslabel{3em}}{\hspace*{-4em}}{~\titlerule*[0.6pc]{$.$}~\contentspage}"
        ]
        
        for command in preamble_commands:
            self.latex_doc.preamble.append(NoEscape(command))
        
        # 定义颜色
        color_definitions = [
            r"\definecolor{blue}{HTML}{3c71b7}",
            r"\definecolor{structurecolor}{HTML}{294C7B}",
            r"\definecolor{blue-deep}{HTML}{294C7B}",
            r"\definecolor{Green-100}{HTML}{F0FFF4}",
            r"\definecolor{Green-200}{HTML}{D2FADF}",
            r"\definecolor{Green-300}{HTML}{A1EDBC}",
            r"\definecolor{Green-400}{HTML}{75E09E}",
            r"\definecolor{Green-500}{HTML}{4CD485}",
            r"\definecolor{Green-700}{HTML}{18A15A}",
            r"\definecolor{Green-800}{HTML}{0C7A45}",
            r"\definecolor{Green-900}{HTML}{045430}",
            r"\definecolor{green}{HTML}{209f59}",
            r"\definecolor{greenback}{HTML}{F0FFF4}",
            r"\definecolor{orange}{HTML}{FF9F43}",
            r"\definecolor{orangeback}{HTML}{FFFAF0}",
            r"\definecolor{red}{HTML}{E84445}",
            r"\definecolor{redback}{HTML}{FFF2F0}"
        ]
        
        for color_def in color_definitions:
            self.latex_doc.append(NoEscape(color_def))
        
        # 添加基本设置
        basic_settings = [
            r"\setcounter{tocdepth}{3}",
            f"\\includepdf[pages=-]{{{PATHS['figure'] / 'cover.pdf'}}}"
        ]
        
        for setting in basic_settings:
            self.latex_doc.append(NoEscape(setting))
        
        # 添加前言、目录和主要内容开始
        self.latex_doc.append(Command("frontmatter"))
        self.latex_doc.append(Command("tableofcontents"))
        self.latex_doc.append(Command("mainmatter"))
        
        # 定义模块样式和计数器
        module_definitions = [
            r"\newtcolorbox{module}[2][]{colback=green!4!white,colframe=green!70!black,colbacktitle=green!70!black,enhanced,attach boxed title to top left={yshift=-2mm,xshift=0.5cm},fonttitle=\bfseries,title={#2},#1}",
            r"\newcounter{little_title}",
            r"\setcounter{little_title}{1}"
        ]
        
        for definition in module_definitions:
            self.latex_doc.append(NoEscape(definition))
    
    def add_document_content(self) -> None:
        """
        将文档内容添加到LaTeX文档中（繁体版）
        """
        if not self.latex_doc:
            raise ValueError("LaTeX文档未初始化，请先调用create_latex_document()")
        
        # 按顺序将字典输入到latex文档中
        for serial, content in self.document_dict.items():
            if content["chapter"] != 0:
                if content["section"] == 0:  # 章节 (1-0-0)
                    self.latex_doc.append(Command("chapter", arguments=content["name"]))
                    self.latex_doc.append(Command("label", content["name"]))
                    self.latex_doc.append(NoEscape(r"\setcounter{little_title}{1}"))
                    
                    if content["text"]:
                        for paragraph in content["text"]:
                            replaced_paragraph = special_character_replacement_traditional(paragraph)
                            syntax_interpreter_traditional(self.latex_doc, replaced_paragraph, serial)
                            
                elif content["subsection"] == 0:  # 节 (1-1-0)
                    self.latex_doc.append(Command("section", arguments=content["name"]))
                    self.latex_doc.append(Command("label", content["name"]))
                    self.latex_doc.append(NoEscape(r"\setcounter{little_title}{1}"))
                    
                    if content["text"]:
                        for paragraph in content["text"]:
                            replaced_paragraph = special_character_replacement_traditional(paragraph)
                            syntax_interpreter_traditional(self.latex_doc, replaced_paragraph, serial)
                            
                else:  # 小节 (1-1-1)
                    self.latex_doc.append(Command("subsection", arguments=content["name"]))
                    self.latex_doc.append(Command("label", content["name"]))
                    self.latex_doc.append(NoEscape(r"\setcounter{little_title}{1}"))
                    
                    if content["text"]:
                        for paragraph in content["text"]:
                            replaced_paragraph = special_character_replacement_traditional(paragraph)
                            syntax_interpreter_traditional(self.latex_doc, replaced_paragraph, serial)
            else:
                print("文件編號錯誤，請先運行文檔處理器")
    
    def generate_tex_file(self, output_dir: str = None) -> str:
        """
        生成tex文件（繁体版）
        
        Args:
            output_dir: 输出目录，默认使用配置中的路径
            
        Returns:
            生成的tex文件路径
        """
        if not self.latex_doc:
            raise ValueError("LaTeX文档未初始化")
        
        if output_dir is None:
            output_dir = str(PATHS["tex_output"])
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成tex文件
        tex_file_path = os.path.join(output_dir, "main_before_traditional.tex")
        self.latex_doc.generate_tex(tex_file_path.replace('.tex', ''))
        
        return tex_file_path
    
    def clean_tex_file(self, tex_file_path: str, output_path: str = None) -> str:
        """
        清理tex文件，删除重复的lastpage包（繁体版）
        
        Args:
            tex_file_path: 输入的tex文件路径
            output_path: 输出的tex文件路径，默认为main_traditional.tex
            
        Returns:
            清理后的tex文件路径
        """
        if output_path is None:
            output_dir = os.path.dirname(tex_file_path)
            output_path = os.path.join(output_dir, "main_traditional.tex")
        
        # 读取并清理文件
        with open(tex_file_path, "r", encoding="utf-8") as f1:
            with open(output_path, "w", encoding="utf-8") as f2:
                for line in f1.readlines():
                    if "lastpage" in line:
                        f2.write("\n")
                    else:
                        f2.write(line)
        
        return output_path
    
    def compile_pdf(self, tex_file_path: str) -> int:
        """
        编译LaTeX文件生成PDF（繁体版）
        
        Args:
            tex_file_path: tex文件路径
            
        Returns:
            编译结果码
        """
        # 切换到tex文件所在目录
        tex_dir = os.path.dirname(tex_file_path)
        tex_filename = os.path.basename(tex_file_path)
        
        original_dir = os.getcwd()
        
        try:
            os.chdir(tex_dir)
            
            # 编译LaTeX
            compile_result = os.system(
                f"latexmk -xelatex -file-line-error -halt-on-error "
                f"-interaction=nonstopmode -synctex=1 {tex_filename}"
            )
            
            # 清理临时文件
            os.system("latexmk -c")
            
            return compile_result
            
        finally:
            os.chdir(original_dir)
    
    def generate_full_latex(self, output_dir: str = None) -> str:
        """
        完整的LaTeX生成流程（繁体版）
        
        Args:
            output_dir: 输出目录
            
        Returns:
            最终PDF文件路径
        """
        print("驗證文檔格式...")
        try:
            self.validate_document_brackets()
            print("文檔格式驗證通過")
        except AssertionError as e:
            print(f"文檔格式驗證失敗: {e}")
            raise
        
        print("創建LaTeX文檔（繁體版）...")
        self.create_latex_document()
        
        print("添加文檔內容...")
        self.add_document_content()
        
        print("生成tex文件...")
        tex_file_path = self.generate_tex_file(output_dir)
        
        print("清理tex文件...")
        clean_tex_path = self.clean_tex_file(tex_file_path)
        
        print("編譯PDF...")
        compile_result = self.compile_pdf(clean_tex_path)
        
        if compile_result == 0:
            pdf_path = clean_tex_path.replace('.tex', '.pdf')
            print(f"PDF生成成功（繁體版）: {pdf_path}")
            return pdf_path
        else:
            print("PDF編譯失敗")
            return ""