import xml.etree.ElementTree as ET

def test_local_xml_parsing():
    # 模拟 XML 内容 (基于你提供的片段)
    # 实际场景中，我们会读取整个文件
    # 这里为了演示核心逻辑，我把你的 XML 片段放进去
    
    xml_path = "/Users/haisen/PostGraduate Folder/副业/ai下单/ctrip_dev/test/resource/ctrip.android.view.debug_ctrip_android_reactnative_preloadv2_CRNBaseActivityV2_page_hierarchy.xml"
    
    print(f"📂 正在读取文件: {xml_path}")
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return

    print("⚡️ 开始解析 XML...")
    root = ET.fromstring(xml_content)
    
    # 构建父节点映射表 (模拟 DynamicXmlLocator)
    parent_map = {c: p for p in root.iter() for c in p}
    
    target_text = "送车上门"
    print(f"🔍 正在寻找: '{target_text}'")

    # 1. 查找文本节点
    found_node = None
    for node in root.iter():
        text = node.attrib.get('text', '')
        res_id = node.attrib.get('resource-id', '')
        
        # 打印一下所有看到的文本，方便调试
        if text:
            # print(f"   -> 扫描到文本: [{text}] ID: [{res_id}]")
            pass

        if target_text in text:
            found_node = node
            print(f"✅ 找到目标文本节点: [{text}]")
            print(f"   - 原始 ID: {res_id}")
            print(f"   - Class: {node.attrib.get('class')}")
            break
    
    if found_node is None:
        print("❌ 未找到目标文本")
        return

    # 2. 向上追溯可点击父级
    print("🚀 开始向上追溯 Clickable 父级...")
    current = found_node
    while current is not None:
        is_clickable = current.attrib.get('clickable') == 'true'
        node_id = current.attrib.get('resource-id', '')
        node_class = current.attrib.get('class', '')
        
        print(f"   ⬆️ 祖先: [{node_class}] ID=[{node_id}] Clickable=[{is_clickable}]")
        
        if is_clickable:
            print(f"🎉 找到最终可点击组件! ID: {node_id}")
            break
        
        current = parent_map.get(current)

if __name__ == "__main__":
    test_local_xml_parsing()
