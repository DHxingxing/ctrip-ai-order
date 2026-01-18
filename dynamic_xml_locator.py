import uiautomator2 as u2
import xml.etree.ElementTree as ET
import time

class DynamicXmlLocator:
    """
    动态 XML 定位器 (进阶版)
    核心能力：
    1. 实时抓取当前页面 XML
    2. 纯内存分析，无需读写文件
    3. 智能寻找：如果目标文字本身不可点，自动向上追溯找到可点击的父容器
    4. 自动生成最佳定位符 (ID优先，XPath兜底)
    """

    def __init__(self, d):
        self.d = d
        self.root = None
        self.parent_map = {}

    def refresh_hierarchy(self):
        """
        刷新当前页面的 XML 结构到内存
        相当于执行了 get_hierarchy.py 的逻辑，但直接在内存处理，不写文件
        """
        print("⚡️ [动态定位] 正在获取当前页面 UI 树 (Dump Hierarchy)...")
        xml_content = self.d.dump_hierarchy()
        try:
            self.root = ET.fromstring(xml_content)
            # 构建父节点映射表，方便后续向上查找
            self.parent_map = {c: p for p in self.root.iter() for c in p}
            print(f"✅ UI 树解析完成，包含 {len(list(self.root.iter()))} 个节点")
        except Exception as e:
            print(f"❌ XML 解析失败: {e}")
            self.root = None
            self.parent_map = {}

    def find_best_selector(self, target_text):
        """
        根据文字，智能返回一个最佳的 uiautomator2 选择器
        """
        if not self.root:
            self.refresh_hierarchy()

        print(f"🔍 在 UI 树中搜索关键词: '{target_text}' ...")

        # 1. 在 XML 树中找到包含文字的节点
        target_node = self._search_node_by_text(self.root, target_text)
        if not target_node:
            print(f"⚠️ [XML分析] 未在当前屏找到文字: {target_text}")
            return None

        # 2. 向上追溯，找到真正的“可点击”组件
        # 很多时候文字只是个 TextView (clickable=false)，真正能点的是它的父容器 Layout
        clickable_node = self._trace_clickable_parent(target_node)
        
        # 3. 提取特征，生成选择器
        selector = self._generate_selector_from_node(clickable_node)
        return selector

    def _search_node_by_text(self, root, text):
        """
        遍历寻找包含文本的节点
        """
        print(f"  > 开始遍历 XML 树查找文本: '{text}'")
        count = 0
        for node in root.iter():
            node_text = node.attrib.get('text', '')
            node_id = node.attrib.get('resource-id', '')
            node_class = node.attrib.get('class', '')
            
            # 简单的包含匹配
            if text in node_text:
                print(f"  ✅ 找到匹配节点! Text='{node_text}', ID='{node_id}', Class='{node_class}'")
                return node
            count += 1
        
        print(f"  ❌ 遍历了 {count} 个节点，未找到包含 '{text}' 的节点")
        return None

    def _trace_clickable_parent(self, node):
        """
        向上回溯，策略优化：
        1. 优先找 clickable="true" 的节点
        2. 如果一路向上都没找到 clickable，则寻找【最近的有 ID 的父节点】
           (React Native 经常出现 clickable=false 但实际通过父级 ID 绑定点击事件的情况)
        """
        current = node
        best_candidate = node # 默认回退到自己
        
        # 记录沿途遇到的第一个有 ID 的节点
        first_node_with_id = None
        
        while current is not None:
            # 1. 检查 clickable 属性
            is_clickable = current.attrib.get('clickable', 'false') == 'true'
            res_id = current.attrib.get('resource-id')
            
            if res_id and not first_node_with_id:
                first_node_with_id = current
            
            if is_clickable:
                print(f"✅ 找到可点击父级: {current.tag} (ID: {res_id})")
                return current
            
            # 向上找爸爸
            current = self.parent_map.get(current)
        
        # 如果一路都没找到 clickable=true
        if first_node_with_id:
            print(f"⚠️ 未找到 Clickable 父级，退而求其次使用最近的有 ID 父级: {first_node_with_id.attrib.get('resource-id')}")
            return first_node_with_id
            
        # 如果连有 ID 的都没找到，那就只能返回原始节点了
        return best_candidate

    def _generate_selector_from_node(self, node):
        """
        根据节点属性生成 u2 选择器
        优先级: resource-id > text > xpath
        """
        # 1. 优先用 ID
        res_id = node.attrib.get('resource-id')
        if res_id:
            # print(f"DEBUG: 使用 ID 定位: {res_id}")
            return self.d(resourceId=res_id)
        
        # 2. 其次用 Text (如果节点本身有 Text)
        text = node.attrib.get('text')
        if text:
            # print(f"DEBUG: 使用 Text 定位: {text}")
            return self.d(text=text)
            
        # 3. 都没有，只能用 Class + Index (比较脆弱，暂不推荐复杂 XPath)
        # 这里做一个简单的兜底：如果没 ID 也没 Text，可能是个图标容器
        # 此时返回 content-desc
        desc = node.attrib.get('content-desc')
        if desc:
            return self.d(description=desc)
            
        return None

