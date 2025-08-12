"""
树结构管理器

提供文档树结构的管理和操作功能
"""

from collections import OrderedDict
from treelib import Tree, Node
from typing import Dict, List, Any, Optional


class TreeManager:
    """树结构管理器类"""
    
    def __init__(self):
        """
        初始化树管理器
        """
        self.tree = Tree()
        
    def create_tree_from_dict(self, document_dict: Dict[str, Any]) -> Tree:
        """
        从文档字典创建树结构
        
        Args:
            document_dict: 文档字典
            
        Returns:
            构建的树结构
        """
        # 创建根节点
        self.tree.create_node(identifier="root", tag="根节点")
        
        # 章节计数器
        chapter_counter = 0
        section_counter = 0
        subsection_counter = 0
        
        for serial in document_dict.keys():
            doc_data = document_dict[serial]
            
            if doc_data["subsection"] == 0:
                if doc_data["section"] == 0:
                    if doc_data["chapter"] == 0:
                        raise NameError(f"文档命名错误：{serial}")
                    else:
                        # 新章节
                        chapter_counter += 1
                        section_counter = 0
                        new_tag = f"{chapter_counter}-0-0"
                        
                        self.tree.create_node(
                            identifier=serial,
                            data=doc_data,
                            tag=new_tag,
                            parent="root"
                        )
                else:
                    # 新节
                    section_counter += 1
                    subsection_counter = 0
                    new_tag = f"{chapter_counter}-{section_counter}-0"
                    
                    # 验证父文档存在
                    father_serial = f"{doc_data['chapter']}-0-0"
                    if father_serial not in document_dict:
                        raise AssertionError(f"{serial} 文档缺少父文档 {father_serial}")
                    
                    self.tree.create_node(
                        identifier=serial,
                        data=doc_data,
                        tag=new_tag,
                        parent=father_serial
                    )
            else:
                # 新小节
                subsection_counter += 1
                new_tag = f"{chapter_counter}-{section_counter}-{subsection_counter}"
                
                # 验证父文档存在
                father_serial = f"{doc_data['chapter']}-{doc_data['section']}-0"
                if father_serial not in document_dict:
                    raise AssertionError(f"{serial} 文档缺少父文档 {father_serial}")
                
                self.tree.create_node(
                    identifier=serial,
                    data=doc_data,
                    tag=new_tag,
                    parent=father_serial
                )
        
        return self.tree
    
    def get_ordered_document_dict(self) -> OrderedDict:
        """
        根据树结构获取有序的文档字典
        
        Returns:
            按树结构排序的文档字典
        """
        ordered_dict = OrderedDict()
        
        # 前序遍历树结构
        for node_id in self.tree.expand_tree(mode=Tree.DEPTH, sorting=False):
            if node_id == self.tree.root:
                continue
                
            node = self.tree[node_id]
            new_serial = node.tag
            doc_data = node.data
            
            # 更新序号
            doc_data["serial"] = new_serial
            chapter, section, subsection = map(int, new_serial.split("-"))
            doc_data["chapter"] = chapter
            doc_data["section"] = section
            doc_data["subsection"] = subsection
            
            ordered_dict[new_serial] = doc_data
        
        return ordered_dict
    
    def show_tree_structure(self) -> None:
        """
        显示树结构
        """
        if self.tree.size() > 0:
            self.tree.show()
        else:
            print("树结构为空")
    
    def get_tree_statistics(self) -> Dict[str, int]:
        """
        获取树结构统计信息
        
        Returns:
            包含统计信息的字典
        """
        if self.tree.size() == 0:
            return {"chapters": 0, "sections": 0, "subsections": 0, "total": 0}
        
        chapters = 0
        sections = 0
        subsections = 0
        
        for node_id in self.tree.expand_tree(mode=Tree.DEPTH, sorting=False):
            if node_id == self.tree.root:
                continue
                
            node = self.tree[node_id]
            tag_parts = node.tag.split("-")
            
            if len(tag_parts) == 3:
                chapter, section, subsection = map(int, tag_parts)
                
                if section == 0 and subsection == 0:
                    chapters += 1
                elif subsection == 0:
                    sections += 1
                else:
                    subsections += 1
        
        return {
            "chapters": chapters,
            "sections": sections,
            "subsections": subsections,
            "total": chapters + sections + subsections
        }
    
    def find_node_by_serial(self, serial: str) -> Optional[Node]:
        """
        根据序号查找节点
        
        Args:
            serial: 文档序号
            
        Returns:
            找到的节点，如果不存在返回None
        """
        try:
            return self.tree.get_node(serial)
        except:
            return None
    
    def get_node_path(self, serial: str) -> List[str]:
        """
        获取节点的路径
        
        Args:
            serial: 文档序号
            
        Returns:
            从根节点到目标节点的路径列表
        """
        try:
            path = []
            current_node = self.tree.get_node(serial)
            
            while current_node and current_node.identifier != self.tree.root:
                path.insert(0, current_node.tag)
                parent_id = self.tree.parent(current_node.identifier)
                current_node = parent_id
            
            return path
        except:
            return []
    
    def get_children_serials(self, serial: str) -> List[str]:
        """
        获取指定节点的所有子节点序号
        
        Args:
            serial: 父节点序号
            
        Returns:
            子节点序号列表
        """
        try:
            children = self.tree.children(serial)
            return [child.tag for child in children]
        except:
            return []