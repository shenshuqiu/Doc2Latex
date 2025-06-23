"""
繁体版文本处理工具函数

提供繁体中文的文本格式转换、特殊字符处理等功能。
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from pylatex import NoEscape, Command, Figure, Itemize, Enumerate

try:
    from opencc import OpenCC
    OPENCC_AVAILABLE = True
except ImportError:
    OPENCC_AVAILABLE = False

from ..config.settings import (
    BOLD_COLOR, L_TITLE_COLOR, LL_TITLE_COLOR, PICTURE_POSITION, 
    PICTURE_WIDTH, BOX_DICT_TRADITIONAL, UNORDERED_LIST_NAME_TRADITIONAL, 
    ORDERED_LIST_NAME_TRADITIONAL, TERM_DICT
)
from .file_utils import image_is_existed


# 初始化简繁转换器（如果可用）
if OPENCC_AVAILABLE:
    cc_s2t = OpenCC('s2t')  # 简体 → 繁体
    cc_t2s = OpenCC('t2s')  # 繁体 → 简体
else:
    cc_s2t = None
    cc_t2s = None


def check_chinese_square_brackets_pairs(text: str) -> bool:
    """
    检查中文方括号是否配对（繁体版）
    
    Args:
        text: 要检查的文本
        
    Returns:
        是否配对正确
    """
    stack = []
    opening_bracket = "【"
    closing_bracket = "】"
    
    for char in text:
        if char == opening_bracket:
            stack.append(char)
        elif char == closing_bracket:
            if len(stack) == 0:
                return False
            last_bracket = stack.pop()
            if last_bracket != opening_bracket:
                return False
    
    return len(stack) == 0


def special_character_replacement_traditional(text: str) -> str:
    """
    将一些特殊字符进行替换（繁体版）
    
    Args:
        text: 原始文本
        
    Returns:
        处理后的文本
    """
    # 替换换行符，屏蔽网站的https://
    text = text.replace("【換行】", r"\\par\n")
    text = re.sub(r"(?<!http:)(?<!https:)//", r"\\par\n", text)
    
    # 替换数学符号
    math_replacements = {
        "%": r"\%",
        "×": r"$\times$",
        "≤": r"$\le$", 
        "≥": r"$\ge$",
        "÷": r"$\div$",
        "≈": r"$\approx$",
        "°": r"$^{\circ}$",
        "->": r"$\rightarrow$",
        "<-": r"$\leftarrow$",
        "℃": r"$^{\circ}$C",
        "Ⅰ": r"\uppercase\expandafter{\romannumeral1}",
        "Ⅱ": r"\uppercase\expandafter{\romannumeral2}",
        "Ⅲ": r"\uppercase\expandafter{\romannumeral3}",
        "Ⅳ": r"\uppercase\expandafter{\romannumeral4}",
        "~": r"$\sim$",
        "&": r"\&",
        "α": r"$\alpha$",
        "β": r"$\beta$",
        "γ": r"$\gamma$",
        "δ": r"$\delta$"
    }
    
    for old_char, new_char in math_replacements.items():
        text = text.replace(old_char, new_char)
    
    # 替换加粗
    text = re.sub(r"【加粗:(.*?)】", rf"\\textbf{{\\textcolor{{{BOLD_COLOR}}}{{\\1}}}}", text)
    text = re.sub(r"【加粗：(.*?)】", rf"\\textbf{{\\textcolor{{{BOLD_COLOR}}}{{\\1}}}}", text)
    
    # 替换引用 - 注意这里使用繁体的"圖"
    if "引用" in text and "-" in text:
        text = text.replace("-", "{-}")
    
    ref_pattern_list = ["【引用:(.*?)】", "【引用：(.*?)】"]
    for ref_pattern in ref_pattern_list:
        for ref_object in re.findall(ref_pattern, text):
            ref_without_pic_pattern = "(?<!圖)" + ref_pattern.replace("(.*?)", ref_object)
            if image_exists_any(ref_object) and re.search(ref_without_pic_pattern, text):
                text = text.replace(ref_pattern.replace("(.*?)", ref_object), r"圖\ref{" + ref_object + r"}")
            else:
                text = text.replace(ref_pattern.replace("(.*?)", ref_object), r"\ref{" + ref_object + r"}")
    
    # 替换网站
    text = re.sub(r"(\b(?:https?://|www\.)\S+\b)", r"\\url{\1}", text)
    
    # 替换术语
    for key, value in TERM_DICT.items():
        text = text.replace(key, value)
    
    return text


def image_exists_any(image_name: str, image_path: str = None) -> bool:
    """
    检查图片是否存在（支持简繁体任意匹配）
    
    Args:
        image_name: 图片名称
        image_path: 图片路径
        
    Returns:
        图片是否存在
    """
    if not OPENCC_AVAILABLE:
        return image_is_existed(image_name, image_path)
    
    # 生成所有可能的变体
    variants = list(set([
        image_name,
        cc_s2t.convert(image_name),
        cc_t2s.convert(image_name)
    ]))
    
    return any(image_is_existed(variant, image_path) for variant in variants)


def syntax_interpreter_traditional(ldoc: Any, string: str, serial: str) -> None:
    """
    将语法字符翻译为latex语法（繁体版）
    
    Args:
        ldoc: LaTeX文档对象
        string: 要处理的字符串
        serial: 文档序号
    """
    if "【" not in string:
        ldoc.append(NoEscape(string))
        ldoc.append(Command("par"))
        return
    else:
        brackets_match = re.search(r"(.*?)【(.*?)】(.*)", string, re.DOTALL)
        pre, content, after = brackets_match.groups()
        colon_match = re.match(r"(.*?)[:：](.*)", content, re.DOTALL)
        
        if colon_match:
            syntax = colon_match.group(1)
            emphasis = colon_match.group(2)
            
            if syntax == "圖片":  # 【圖片：圖片名稱】
                assert image_exists_any(emphasis), f"{serial}的{emphasis}圖片不存在"
                syntax_interpreter_traditional(ldoc, pre, serial)
                
                # 标签统一使用繁体
                emphasis_trad = cc_s2t.convert(emphasis) if OPENCC_AVAILABLE else emphasis
                
                with ldoc.create(Figure(position=PICTURE_POSITION)) as pic:
                    pic.add_image(f"data/assets/image/{emphasis}", width=PICTURE_WIDTH)
                    if after == "":
                        pic.add_caption(emphasis)
                    else:
                        pic.add_caption(after)
                    ldoc.append(Command("label", emphasis_trad))
                return
                
            elif syntax == "小標題":
                syntax_interpreter_traditional(ldoc, pre, serial)
                ldoc.append(NoEscape(r"\vspace{1ex}"))
                ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{L_TITLE_COLOR}}}{{\large \arabic{{little_title}}、{emphasis}}}}}"))
                ldoc.append(Command("par"))
                ldoc.append(NoEscape(r"\refstepcounter{little_title}"))
                ldoc.append(NoEscape(r"\vspace{1ex}"))
                syntax_interpreter_traditional(ldoc, after, serial)
                
            elif syntax == "小小標題":
                syntax_interpreter_traditional(ldoc, pre, serial)
                ldoc.append(NoEscape(r"\vspace{0.4ex}"))
                ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{LL_TITLE_COLOR}}}{{ {emphasis}}}}}"))
                ldoc.append(Command("par"))
                ldoc.append(NoEscape(r"\vspace{0.4ex}"))
                syntax_interpreter_traditional(ldoc, after, serial)
                
            elif syntax in BOX_DICT_TRADITIONAL.keys():
                syntax_interpreter_traditional(ldoc, pre, serial)
                color = BOX_DICT_TRADITIONAL[syntax]
                col_color = f"colback={color}back,colframe={color},colbacktitle={color}"
                ldoc.append(NoEscape(r"\begin{module}[" + col_color + r"]{" + syntax + r"}"))
                
                # 标签统一使用繁体
                emphasis_trad = cc_s2t.convert(emphasis) if OPENCC_AVAILABLE else emphasis
                ldoc.append(NoEscape(r"\label{" + emphasis_trad + r"}"))
                ldoc.append(NoEscape(r"\textbf{\large " + emphasis + "}"))
                ldoc.append(NoEscape(r"\tcblower"))
                syntax_interpreter_traditional(ldoc, after.replace(BOLD_COLOR, color), serial)
                ldoc.append(NoEscape(r"\end{module}"))
            else:
                raise TypeError(f"{serial}中的語法{syntax}未定義")
                
        elif content in UNORDERED_LIST_NAME_TRADITIONAL:
            syntax_interpreter_traditional(ldoc, pre, serial)
            with ldoc.create(Itemize()) as itemize:
                for item in re.split(r"[;；]", after):
                    if item != "":
                        itemize.add_item(NoEscape(item))
            ldoc.append(Command("par"))
            
        elif content in ORDERED_LIST_NAME_TRADITIONAL:
            syntax_interpreter_traditional(ldoc, pre, serial)
            with ldoc.create(Enumerate()) as enum:
                for item in re.split(r"[;；]", after):
                    if item != "":
                        enum.add_item(NoEscape(item))
            ldoc.append(Command("par"))
            
        elif content == "小標題":
            syntax_interpreter_traditional(ldoc, pre, serial)
            ldoc.append(NoEscape(r"\vspace{1ex}"))
            ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{L_TITLE_COLOR}}}{{\large \arabic{{little_title}}、{after}}}}}"))
            ldoc.append(Command("par"))
            ldoc.append(NoEscape(r"\refstepcounter{little_title}"))
            ldoc.append(NoEscape(r"\vspace{1ex}"))
            ldoc.append(Command("par"))
            
        elif content == "小小標題":
            syntax_interpreter_traditional(ldoc, pre, serial)
            ldoc.append(NoEscape(r"\vspace{0.4ex}"))
            ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{LL_TITLE_COLOR}}}{{ {after}}}}}"))
            ldoc.append(Command("par"))
            ldoc.append(NoEscape(r"\vspace{0.4ex}"))
            ldoc.append(Command("par"))
            
        elif content in BOX_DICT_TRADITIONAL.keys():
            syntax_interpreter_traditional(ldoc, pre, serial)
            color = BOX_DICT_TRADITIONAL[content]
            col_color = f"colback={color}back,colframe={color},colbacktitle={color}"
            ldoc.append(NoEscape(r"\begin{module}[" + col_color + r"]{" + content + r"}"))
            syntax_interpreter_traditional(ldoc, after.replace(BOLD_COLOR, color), serial)
            ldoc.append(NoEscape(r"\end{module}"))
        else:
            raise TypeError(f"{serial}中的語法{content}未定義")