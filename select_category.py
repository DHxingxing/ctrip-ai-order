import uiautomator2 as u2
import time

class FastFilterExecutor:
    def __init__(self, d):
        self.d = d
        # 记录本轮已处理的词
        self.processed_keywords = set()

    def _is_true(self, val):
        if isinstance(val, bool): return val
        return str(val).lower() == 'true'

    def _parse_bounds(self, bounds_val):
        """
        解析 bounds，支持:
        1. UiObject dict: {'top': 100, 'bottom': 200, ...}
        2. XPath tuple: (l, t, r, b)
        3. XPath string: "[100,200][300,400]"
        """
        try:
            if isinstance(bounds_val, dict):
                return bounds_val.get('left'), bounds_val.get('top'), bounds_val.get('right'), bounds_val.get('bottom')
            
            if isinstance(bounds_val, (list, tuple)) and len(bounds_val) == 4:
                return bounds_val
            
            if isinstance(bounds_val, str):
                import re
                # 匹配 [x1,y1][x2,y2]
                m = re.findall(r'\d+', bounds_val)
                if len(m) == 4:
                    return int(m[0]), int(m[1]), int(m[2]), int(m[3])
        except:
            pass
        return None

    def _is_element_selected(self, element, text="Unknown"):
        """
        判断是否已选中
        增强版：兼容 XPathElement 和 UiObject，检查自身及父级
        """
        try:
            # 1. 获取自身属性
            # XPathElement 用 .attrib, UiObject 用 .info
            info = {}
            if hasattr(element, 'info'): info.update(element.info)
            if hasattr(element, 'attrib'): info.update(element.attrib)
            
            is_checked = self._is_true(info.get('checked'))
            is_selected = self._is_true(info.get('selected'))
            
            if is_checked or is_selected:
                print(f"DEBUG: [{text}] 自身已选中 (checked={is_checked}, selected={is_selected})")
                return True
            
            # 2. 检查父容器 (仅向上查一层，防止误判)
            parent = None
            try:
                if hasattr(element, 'parent'): # XPathElement
                    parent = element.parent()
                elif hasattr(element, 'up'): # UiObject
                    parent = element.up()
            except: pass

            if parent:
                p_info = {}
                if hasattr(parent, 'info'): p_info.update(parent.info)
                if hasattr(parent, 'attrib'): p_info.update(parent.attrib)
                
                p_checked = self._is_true(p_info.get('checked'))
                p_selected = self._is_true(p_info.get('selected'))
                
                if p_checked or p_selected:
                    print(f"DEBUG: [{text}] 父级已选中 (checked={p_checked}, selected={p_selected})")
                    return True
                    
            return False
        except Exception as e:
            # print(f"DEBUG: check selection failed {e}")
            return False

    def _get_parent_info(self, element):
        """
        尝试获取父级元素信息
        """
        try:
            parent = None
            if hasattr(element, 'parent'): # XPathElement
                parent = element.parent()
            elif hasattr(element, 'up'): # UiObject
                parent = element.up()
            
            if parent:
                info = {}
                if hasattr(parent, 'info'): info.update(parent.info)
                if hasattr(parent, 'attrib'): info.update(parent.attrib)
                return info
        except:
            pass
        return {}

    def _get_element_score(self, element, text):
        """
        【智能评分系统】
        为每个候选元素打分，分数最高的才是真身。
        """
        score = 0
        reasons = []

        try:
            # 1. 基础信息获取
            info = {}
            if hasattr(element, 'info'): info.update(element.info)
            if hasattr(element, 'attrib'): info.update(element.attrib)
            
            p_info = self._get_parent_info(element)
            
            # 2. 坐标分析 (Geometry)
            bounds_val = info.get('bounds')
            parsed_bounds = self._parse_bounds(bounds_val)
            
            if parsed_bounds:
                l, t, r, b = parsed_bounds
                w, h = self.d.window_size()
                center_x = (l + r) / 2
                center_y = (t + b) / 2
                width = r - l
                height = b - t

                # A. 侧边栏惩罚 (Left Sidebar Penalty)
                if center_x < w * 0.25:
                    score -= 50
                    reasons.append("sidebar_penalty")
                else:
                    score += 10
                    reasons.append("main_content_bonus")

                # B. 标题栏惩罚 (Header Penalty)
                # 标题通常很宽 (占满屏幕)，且高度较小
                if width > w * 0.9:
                    score -= 20
                    reasons.append("full_width_penalty")
                
                # C. 选项框特征 (Box Feature)
                # 选项通常有合理的宽高比，不会太扁
                if height > 50: 
                    score += 10
                    reasons.append("valid_height_bonus")

            # 3. 结构分析 (Structure)
            p_class = p_info.get('className', '')
            
            # D. 容器奖励 (Container Bonus)
            # 有效选项通常包裹在 ViewGroup / LinearLayout 中
            if 'ViewGroup' in p_class or 'LinearLayout' in p_class:
                score += 20
                reasons.append("container_bonus")
            
            # E. 列表容器惩罚 (List Container Penalty)
            # 直接在 RecyclerView 下的 TextView 通常是标题或状态
            if 'RecyclerView' in p_class or 'ListView' in p_class:
                score -= 30
                reasons.append("direct_list_child_penalty")

            # 4. 属性分析 (Attribute)
            # F. 可点击奖励 (Clickable Bonus)
            # 虽然有些选项 clickable=false，但如果它(或父级)是 true，那肯定是加分项
            is_self_clickable = self._is_true(info.get('clickable'))
            is_parent_clickable = self._is_true(p_info.get('clickable'))
            
            if is_self_clickable:
                score += 15
                reasons.append("self_clickable")
            if is_parent_clickable:
                score += 15
                reasons.append("parent_clickable")
            
            # G. 选中状态 (State)
            # 如果已经 checked，说明它肯定是选项 (标题不会 checked)
            if self._is_true(info.get('checked')) or self._is_true(p_info.get('checked')):
                score += 50
                reasons.append("is_checkable_item")

        except Exception as e:
            print(f"⚠️ 评分异常: {e}")
        
        return score, reasons

    def _smart_click(self, element, text):
        """
        【核心修复】双重点击策略 + 智能评分
        """
        try:
            # === 新增：智能评分验证 ===
            # 如果当前页面有多个相同的 text，我们需要比较它们
            # 但这里我们只拿到了一个 element，所以我们只能判断“它是否足够好”
            # 或者，我们在上层循环时就应该做最佳匹配。
            # 为了兼容现有逻辑，我们在这里做一个“及格线”判断
            
            score, reasons = self._get_element_score(element, text)
            print(f"📊 [{text}] 评分: {score} 原因: {reasons}")
            
            # 设定及格线 (Threshold)
            # 侧边栏通常得分: -50 (sidebar) + 20 (container) = -30
            # 纯标题通常得分: -20 (full_width) + 20 (container) = 0
            # 有效选项通常得分: 10 (main) + 10 (height) + 20 (container) + 15 (parent_clickable?) = 40~55
            
            if score < 10:
                print(f"🚫 [{text}] 评分过低 ({score})，跳过")
                return False

            # 1. 解析坐标
            bounds_val = None
            if hasattr(element, 'info'):
                bounds_val = element.info.get('bounds')
            if not bounds_val and hasattr(element, 'attrib'):
                bounds_val = element.attrib.get('bounds')
            
            l, t, r, b = 0, 0, 0, 0
            parsed_bounds = self._parse_bounds(bounds_val)
            if parsed_bounds:
                l, t, r, b = parsed_bounds
            
            # 2. 状态检查
            if self._is_element_selected(element, text):
                print(f"🛡️ [{text}] 已处于选中状态，跳过操作")
                self.processed_keywords.add(text)
                return True

            print(f"👉 尝试点击目标: [{text}] (Bounds: {l},{t},{r},{b})")
            
            # === 动作: 精确点击中心 ===
            if l and r and t and b:
                center_x = (l + r) / 2
                center_y = (t + b) / 2
                self.d.click(center_x, center_y)
            else:
                element.click()
            
            # 记录已处理
            self.processed_keywords.add(text)
            return True
            
        except Exception as e:
            print(f"❌ 点击异常 {text}: {e}")
            return False

    def execute(self, user_keywords):
        print(f"🚀 启动强力筛选，目标: {user_keywords}")
        
        # 1. 进筛选页 (明确点击 "更多筛选")
        if not self.d(text="完成").exists:
            print("🔍 寻找入口: [更多筛选]")
            # 优先精确匹配，防止点错
            filter_btn = self.d(text="更多筛选")
            if not filter_btn.exists:
                filter_btn = self.d(textContains="筛选")
            
            if filter_btn.exists:
                filter_btn.click()
                time.sleep(1.5)
            else:
                print("❌ 未找到筛选入口")
                return

        # 2. 归位
        # 尝试查找可滚动元素并置顶
        scroller = self.d(scrollable=True)
        if scroller.exists:
            scroller.scroll.toBeginning()
            time.sleep(0.5)

        w, h = self.d.window_size()
        last_page_source = ""
        
        # 3. 循环扫描 (最大 15 轮)
        for i in range(15):
            print(f"--- 🔄 扫描第 {i+1} 屏 ---")
            
            # A. 优先处理展开 (防止漏掉折叠内容)
            self.d.implicitly_wait(0.5) # 降低等待时间提升效率
            expand_btns = self.d(text="展开")
            if expand_btns.exists:
                try:
                    # 遍历当前页所有展开按钮
                    for btn in expand_btns:
                        print("📂 点击 [展开]")
                        btn.click()
                        time.sleep(0.5)
                except: pass

            # B. 批量查找关键词 (极速模式)
            # 获取当前屏幕所有 TextView，一次性比对，避免多次 RPC 调用
            visible_texts = self.d.xpath('//android.widget.TextView').all()
            
            found_any_in_this_page = False
            
            for el in visible_texts:
                try:
                    el_text = el.text
                    if not el_text: continue
                    
                    # 检查是否包含在目标关键词中
                    matched_keyword = None
                    for kw in user_keywords:
                        if kw in self.processed_keywords:
                            continue
                        if kw in el_text:
                            matched_keyword = kw
                            break
                    
                    if matched_keyword:
                        # 找到目标，执行点击
                        if self._smart_click(el, matched_keyword):
                            found_any_in_this_page = True
                            time.sleep(0.2) # 微小延迟
                except:
                    continue

            # C. 检查任务完成度
            if len(self.processed_keywords) >= len(user_keywords):
                print(f"🎉 全部目标已选中！耗时: {i+1} 屏")
                break

            # D. 大幅滑动 (如果没有找齐)
            # 到底检测：对比页面内容摘要
            current_nodes = self.d.xpath('//android.widget.TextView').all()
            # 仅取前10个和后10个元素的文本作为指纹，提高效率
            node_texts = [n.text for n in current_nodes]
            current_page_source = "".join(node_texts[:10] + node_texts[-10:])
            
            if current_page_source == last_page_source:
                print("🛑 到底了，停止滑动")
                break
            last_page_source = current_page_source

            print("👇 快速翻页...")
            # 稍微加快滑动速度 duration=0.3
            self.d.swipe(w*0.5, h*0.8, w*0.5, h*0.3, duration=0.3)
            time.sleep(0.8) # 滑动后等待时间缩短

        # 4. 提交
        print(f"📊 最终选中: {list(self.processed_keywords)}")
        if self.d(text="完成").exists:
            self.d(text="完成").click()
        else:
            # 备用点击右下角
            self.d.click(w * 0.9, h * 0.95)

# ================= 测试入口 =================
if __name__ == '__main__':
    d = u2.connect()
    
    # 你的目标列表
    user_input = ["送车上门", "自助取还", "不限里程", "积分当钱花", "身份证", "免费取消","春节大促"]
    
    executor = FastFilterExecutor(d)
    executor.execute(user_input)