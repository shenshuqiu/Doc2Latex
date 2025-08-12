"""
文本处理工具函数

提供文本格式转换、特殊字符处理等功能。
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from pylatex import NoEscape, Command, Figure, Itemize, Enumerate

from ..config.settings import (
    BOLD_COLOR, L_TITLE_COLOR, LL_TITLE_COLOR, PICTURE_POSITION, 
    PICTURE_WIDTH, BOX_DICT, UNORDERED_LIST_NAME, ORDERED_LIST_NAME, TERM_DICT
)
from .file_utils import image_is_existed, get_image_filename_with_extension
from .logger import get_logger


def check_chinese_square_brackets_pairs(text: str) -> bool:
    """
    检查中文方括号是否配对
    
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


def smart_split_list_items(text: str) -> List[str]:
    """
    智能分割列表项，避免破坏URL命令和其他结构
    
    Args:
        text: 要分割的文本
        
    Returns:
        分割后的列表项
    """
    items = []
    current_item = ""
    url_depth = 0
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # 检查是否进入URL命令
        if text[i:i+5] == '\\url{':
            url_depth += 1
            current_item += text[i:i+5]
            i += 5
            continue
        
        # 检查是否退出URL命令
        if char == '}' and url_depth > 0:
            url_depth -= 1
            current_item += char
            i += 1
            continue
        
        # 检查分隔符
        if char in ';；' and url_depth == 0:
            if current_item.strip():
                items.append(current_item.strip())
            current_item = ""
            i += 1
            continue
        
        current_item += char
        i += 1
    
    # 添加最后一项
    if current_item.strip():
        items.append(current_item.strip())
    
    return items


def validate_syntax_patterns(text: str, serial: str = "") -> List[str]:
    """
    验证语法模式，检测可能的引用格式错误
    
    Args:
        text: 要检查的文本
        serial: 文档序号
        
    Returns:
        错误信息列表
    """
    errors = []
    
    # 检查嵌套的\url{}命令
    if r'\url{' in text and r'\url{\url{' in text:
        errors.append(f"{serial}: 检测到嵌套的URL命令，可能导致编译失败")
    
    # 检查不匹配的\url{}括号
    url_pattern = r'\\url\{[^}]*$'
    if re.search(url_pattern, text, re.MULTILINE):
        errors.append(f"{serial}: 检测到不完整的URL命令（缺少闭合括号）")
    
    # 检查引用格式错误
    invalid_ref_patterns = [
        r'\\ref\{[^}]*\\',  # ref命令中包含反斜杠
        r'\\url\{[^}]*\\url\{',  # URL命令嵌套
    ]
    
    for pattern in invalid_ref_patterns:
        if re.search(pattern, text):
            errors.append(f"{serial}: 检测到严重的引用格式错误: {pattern}")
    
    # 检查连续引用（警告级别，不阻断编译）
    consecutive_refs = re.findall(r'【引用：[^】]*】【引用：[^】]*】', text)
    if consecutive_refs:
        # 这只是警告，不加入errors列表
        logger = get_logger()
        logger.warning(f"{serial}: 检测到连续引用标记，建议添加分隔符: {len(consecutive_refs)}处")
    
    # 检查连续的语法标记
    consecutive_syntax = r'】【'
    matches = re.findall(consecutive_syntax, text)
    if len(matches) > 3:  # 允许少量连续语法，但过多可能有问题
        errors.append(f"{serial}: 检测到过多连续语法标记，可能导致解析错误")
    
    return errors


def special_character_replacement(text: str) -> str:
    """
    将一些特殊字符进行替换
    
    Args:
        text: 原始文本
        
    Returns:
        处理后的文本
    """
    # 替换换行符，屏蔽网站的https://
    text = text.replace("【换行】", r"\\par\n")
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
    def bold_replacement(match):
        content = match.group(1).strip()
        if content:
            return f"\\textbf{{\\textcolor{{{BOLD_COLOR}}}{{{content}}}}}"
        else:
            return ""  # 空内容直接忽略
    
    text = re.sub(r"【加粗:(.*?)】", bold_replacement, text)
    text = re.sub(r"【加粗：(.*?)】", bold_replacement, text)
    
    # 替换脚注
    def footnote_replacement(match):
        content = match.group(1).strip()
        if content:
            return f"\\footnote{{{content}}}"
        else:
            return ""  # 空内容直接忽略
    
    text = re.sub(r"【脚注:(.*?)】", footnote_replacement, text)
    text = re.sub(r"【脚注：(.*?)】", footnote_replacement, text)
    
    # 替换引用
    if "引用" in text and "-" in text:
        text = text.replace("-", "{-}")
    
    ref_pattern_list = ["【引用:(.*?)】", "【引用：(.*?)】"]
    for ref_pattern in ref_pattern_list:
        for ref_object in re.findall(ref_pattern, text):
            ref_without_pic_pattern = "(?<!图)" + ref_pattern.replace("(.*?)", ref_object)
            if image_is_existed(ref_object) and re.search(ref_without_pic_pattern, text):
                text = text.replace(ref_pattern.replace("(.*?)", ref_object), r"图\ref{" + ref_object + r"}")
            else:
                text = text.replace(ref_pattern.replace("(.*?)", ref_object), r"\ref{" + ref_object + r"}")
    
    # 替换网站 - 统一处理所有URL，避免重复处理
    def url_replacement(match):
        url = match.group(0)
        # 如果URL已经被\url{}包围，就不再处理
        if '\\url{' in url:
            return url
        return f"\\url{{{url}}}"
    
    text = re.sub(r"\b(?:https?://|www\.)\S+", url_replacement, text)
    
    # 替换术语
    for key, value in TERM_DICT.items():
        text = text.replace(key, value)
    
    return text


def syntax_interpreter(ldoc: Any, string: str, serial: str, document_processor=None) -> None:
    """
    将语法字符翻译为latex语法,并写入ldoc
    
    Args:
        ldoc: LaTeX文档对象
        string: 要处理的字符串
        serial: 文档序号
    """
    # 在处理前进行语法验证
    validation_errors = validate_syntax_patterns(string, serial)
    if validation_errors:
        logger = get_logger()
        for error in validation_errors:
            logger.warning(error)
        # 如果有严重错误（如嵌套URL），抛出异常
        if any("嵌套的URL命令" in error or "不完整的URL命令" in error for error in validation_errors):
            raise ValueError(f"{serial}: 检测到严重的语法错误，可能导致LaTeX编译失败")
    
    # 递归式地将所有包含【】的语法翻译
    # 无【】语法
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
            
            if syntax == "图片":  # 【图片：图片名称】
                assert image_is_existed(emphasis), f"{serial}的{emphasis}图片不存在"
                syntax_interpreter(ldoc, pre, serial, document_processor)
                # 获取带扩展名的完整文件名
                full_image_name = get_image_filename_with_extension(emphasis)
                with ldoc.create(Figure(position=PICTURE_POSITION)) as pic:
                    pic.add_image(f"../../../../data/assets/image/{full_image_name}", width=PICTURE_WIDTH)
                    if after == "":
                        pic.add_caption(emphasis)
                    else:
                        pic.add_caption(after)
                    ldoc.append(Command("label", emphasis))
                return
                
            elif syntax == "小标题":
                syntax_interpreter(ldoc, pre, serial, document_processor)
                ldoc.append(NoEscape(r"\vspace{1ex}"))
                ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{L_TITLE_COLOR}}}{{\large \arabic{{little_title}}、{emphasis}}}}}"))
                ldoc.append(Command("par"))
                ldoc.append(NoEscape(r"\refstepcounter{little_title}"))
                ldoc.append(NoEscape(r"\vspace{1ex}"))
                syntax_interpreter(ldoc, after, serial, document_processor)
                
            elif syntax == "小小标题":
                syntax_interpreter(ldoc, pre, serial, document_processor)
                ldoc.append(NoEscape(r"\vspace{0.4ex}"))
                ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{LL_TITLE_COLOR}}}{{ {emphasis}}}}}"))
                ldoc.append(Command("par"))
                ldoc.append(NoEscape(r"\vspace{0.4ex}"))
                syntax_interpreter(ldoc, after, serial, document_processor)
                
            elif syntax == "加粗":  # 【加粗：文本内容】
                syntax_interpreter(ldoc, pre, serial, document_processor)
                ldoc.append(NoEscape(rf"\textbf{{{emphasis}}}"))
                syntax_interpreter(ldoc, after, serial, document_processor)
                
            elif syntax == "脚注":  # 【脚注：脚注内容】
                syntax_interpreter(ldoc, pre, serial, document_processor)
                ldoc.append(NoEscape(rf"\footnote{{{emphasis}}}"))
                syntax_interpreter(ldoc, after, serial, document_processor)
                
                
            elif syntax in BOX_DICT.keys():
                syntax_interpreter(ldoc, pre, serial, document_processor)
                color = BOX_DICT[syntax]
                col_color = f"colback={color}back,colframe={color},colbacktitle={color}"
                ldoc.append(NoEscape(r"\begin{module}[" + col_color + r"]{" + syntax + r"}"))
                ldoc.append(NoEscape(r"\label{" + emphasis + r"}"))
                ldoc.append(NoEscape(r"\textbf{\large " + emphasis + "}"))
                ldoc.append(NoEscape(r"\tcblower"))
                syntax_interpreter(ldoc, after.replace(BOLD_COLOR, color), serial, document_processor)
                ldoc.append(NoEscape(r"\end{module}"))
            else:
                logger = get_logger()
                suggestions = []
                
                # 提供建议
                if "标题" in syntax:
                    suggestions.append("使用【小标题：标题内容】或【小小标题：标题内容】")
                elif "弹力带" in syntax or "髋关节" in syntax:
                    suggestions.append("使用【加粗：弹力带髋关节松动】进行加粗显示")
                elif "小标退" in syntax:
                    suggestions.append("应该是【小标题】，请检查文档中的错别字")
                else:
                    suggestions.extend([
                        "检查语法是否正确",
                        "参考支持的语法：【小标题】、【图片：名称】、【加粗：内容】等"
                    ])
                
                logger.report_syntax_error(serial, syntax, suggestions)
                raise TypeError(f"{serial}中的语法{syntax}未定义")
                
        elif content in UNORDERED_LIST_NAME:
            syntax_interpreter(ldoc, pre, serial, document_processor)
            with ldoc.create(Itemize()) as itemize:
                # 智能分割，避免破坏URL命令
                items = smart_split_list_items(after)
                for item in items:
                    if item.strip():
                        itemize.add_item(NoEscape(item.strip()))
            ldoc.append(Command("par"))
            
        elif content in ORDERED_LIST_NAME:
            syntax_interpreter(ldoc, pre, serial, document_processor)
            with ldoc.create(Enumerate()) as enum:
                # 智能分割，避免破坏URL命令
                items = smart_split_list_items(after)
                for item in items:
                    if item.strip():
                        enum.add_item(NoEscape(item.strip()))
            ldoc.append(Command("par"))
            
        elif content == "小标题":
            syntax_interpreter(ldoc, pre, serial, document_processor)
            ldoc.append(NoEscape(r"\vspace{1ex}"))
            ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{L_TITLE_COLOR}}}{{\large \arabic{{little_title}}、{after}}}}}"))
            ldoc.append(Command("par"))
            ldoc.append(NoEscape(r"\refstepcounter{little_title}"))
            ldoc.append(NoEscape(r"\vspace{1ex}"))
            ldoc.append(Command("par"))
            
        elif content == "小小标题":
            syntax_interpreter(ldoc, pre, serial, document_processor)
            ldoc.append(NoEscape(r"\vspace{0.4ex}"))
            ldoc.append(NoEscape(rf"\textbf{{\textcolor{{{LL_TITLE_COLOR}}}{{ {after}}}}}"))
            ldoc.append(Command("par"))
            ldoc.append(NoEscape(r"\vspace{0.4ex}"))
            ldoc.append(Command("par"))
            
            
        elif content in BOX_DICT.keys():
            syntax_interpreter(ldoc, pre, serial, document_processor)
            color = BOX_DICT[content]
            col_color = f"colback={color}back,colframe={color},colbacktitle={color}"
            ldoc.append(NoEscape(r"\begin{module}[" + col_color + r"]{" + content + r"}"))
            syntax_interpreter(ldoc, after.replace(BOLD_COLOR, color), serial, document_processor)
            ldoc.append(NoEscape(r"\end{module}"))
        else:
            # 检查是否没有冒号分隔符，如果没有则当作默认加粗处理
            if ":" not in content and "：" not in content:
                # 默认当作加粗处理：【内容】 等价于 【加粗:内容】
                syntax_interpreter(ldoc, pre, serial, document_processor)
                ldoc.append(NoEscape(f"\\textbf{{\\textcolor{{{BOLD_COLOR}}}{{{content}}}}}"))
                syntax_interpreter(ldoc, after, serial, document_processor)
            else:
                # 有冒号但不匹配任何语法，报告错误
                logger = get_logger()
                suggestions = []
                
                # 提供建议
                if "标题" in content:
                    suggestions.append("使用【小标题】或【小标题：内容】")
                elif "弹力带" in content or "髋关节" in content:
                    suggestions.append("使用【加粗：弹力带髋关节松动】进行加粗显示")
                elif "小标退" in content:
                    suggestions.append("应该是【小标题】，请检查文档中的错别字")
                else:
                    suggestions.extend([
                        "检查语法是否正确",
                        "参考支持的语法：【小标题】、【图片：名称】、【加粗：内容】等"
                    ])
                
                # 构建错误信息，包含原始文件名
                if document_processor and hasattr(document_processor, 'get_original_filename'):
                    original_serial = document_processor.get_original_filename(serial)
                    if original_serial != serial:
                        error_serial = f"{serial}(原{original_serial})"
                    else:
                        error_serial = serial
                else:
                    error_serial = serial
                
                logger.report_syntax_error(error_serial, content, suggestions)
                raise TypeError(f"{error_serial}中的语法{content}未定义")