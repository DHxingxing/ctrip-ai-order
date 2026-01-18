import uiautomator2 as u2
import time

class SmartFilter:
    """
    通用智能筛选器 (正则匹配版)
    利用 car_testid_comp_filter_modal_item_ 通用前缀，配合滚动操作，
    实现对任意选项（价格、服务、车型、供应商）的精准点击。
    """
    def __init__(self, d):
        self.d = d
        self.processed_keywords = set()

    def select_options(self, target_keywords):
        """
        执行筛选任务（滚动 + 正则匹配）
        :param target_keywords: 想要点击的关键词列表
        """
        print(f"🚀 [智能筛选] 开始任务，目标: {target_keywords}")
        
        # 1. 确保在筛选页
        self._ensure_filter_page_open()
        
        # 2. 循环扫描 (滚动查找)
        # 最多滑 10 次，防止无限循环
        max_swipes = 10
        
        for i in range(max_swipes):
            print(f"--- 🔄 扫描第 {i+1} 屏 ---")
            
            # 执行当前屏的匹配点击
            # 返回值: layout_changed (bool) - 指示是否发生了展开操作
            layout_changed = self._process_current_screen(target_keywords)
            
            # 检查是否全部完成
            if len(self.processed_keywords) >= len(target_keywords):
                print("🎉 所有目标都已找到并点击！")
                break
            
            # 策略调整：如果发生了布局变化（点击了展开），我们不要急着翻页
            # 而是应该“原地重试”甚至“往回找找”，防止新出现的内容被挤出屏幕
            if layout_changed:
                print("⚠️ 检测到页面展开，执行【回溯扫描】防止漏选...")
                # 向上微滑 (把可能被顶上去的内容拉回来)
                self.d.swipe(0.5, 0.4, 0.5, 0.6, duration=0.3)
                time.sleep(1.0)
                continue # 跳过本次翻页，重新扫描当前位置
            
            # 正常滑动翻页
            print("👇 向下滑动寻找剩余选项...")
            # 从屏幕 80% 处滑到 30% 处，幅度适中
            self.d.swipe(0.5, 0.8, 0.5, 0.3, duration=0.5)
            time.sleep(1.5) # 滑动后等待页面稳定
            
        print(f"📊 筛选结束，已选中: {list(self.processed_keywords)}")
        
        # 3. 点击完成
        self._click_finish()

    def _process_current_screen(self, target_keywords):
        """
        处理当前屏幕上的所有选项
        :return: bool 是否发生了“展开”操作
        """
        has_expanded = False
        
        # --- 步骤 0: 先把所有的“展开”按钮点开 ---
        # 很多选项藏在折叠区域里，必须先展开才能被 resourceIdMatches 抓到
        try:
            # 查找所有文本为“展开”的按钮
            expand_btns = self.d(text="展开")
            if expand_btns.exists:
                print("📂 发现折叠区域，正在全部展开...")
                # 遍历点击每一个展开按钮
                for btn in expand_btns:
                    try:
                        # 只有当按钮在屏幕内才点
                        if btn.info['bounds']['bottom'] < self.d.window_size()[1]:
                            btn.click()
                            has_expanded = True
                            time.sleep(0.5) # 等待展开动画
                    except:
                        pass
                if has_expanded:
                    print("✅ 折叠区域已展开 (触发重扫机制)")
                    return True # 立即返回，通知外层重扫，因为坐标全变了
        except:
            pass

        # --- 步骤 1: 扫描选项 ---
        # 匹配所有 ID 以 car_testid_comp_filter_modal_item_ 开头的元素
        # 这是一个非常棒的特征，携程开发留下的“后门”
        try:
            all_options = self.d(resourceIdMatches=".*car_testid_comp_filter_modal_item_.*")
            count = len(all_options)
            if count == 0:
                print("⚠️ 当前屏未识别到任何 filter_modal_item")
                return
        except:
            return

        # 遍历所有找到的“格子”
        for item in all_options:
            try:
                # 在格子（ViewGroup）里找文字（TextView）
                # 注意：有些格子可能结构复杂，我们找第一个 TextView
                child_text = item.child(className="android.widget.TextView")
                
                if child_text.exists:
                    text_content = child_text.info['text']
                    
                    # 检查是否已处理过
                    matched_kw = None
                    for kw in target_keywords:
                        if kw in text_content:
                            matched_kw = kw
                            break
                    
                    if matched_kw and matched_kw not in self.processed_keywords:
                        print(f"✅ 找到目标: 【{text_content}】 (匹配关键词: {matched_kw})")
                        
                        # 坐标点击 (最稳)
                        bounds = item.info['bounds']
                        cx = (bounds['left'] + bounds['right']) / 2
                        cy = (bounds['top'] + bounds['bottom']) / 2
                        
                        # 屏幕内检测
                        screen_h = self.d.window_size()[1]
                        if 0 < cy < screen_h:
                            print(f"👆 点击坐标: ({cx}, {cy})")
                            self.d.click(cx, cy)
                            self.processed_keywords.add(matched_kw)
                            time.sleep(0.5) 
                        else:
                            print("⚠️ 元素在屏幕外，跳过")
            except:
                pass

    def _ensure_filter_page_open(self):
        """
        确保筛选页已打开
        """
        if not self.d(text="完成").exists:
            print("🔍 尝试打开筛选面板...")
            if self.d(text="更多筛选").exists:
                self.d(text="更多筛选").click()
            elif self.d(textContains="筛选").exists:
                self.d(textContains="筛选").click()
            time.sleep(1.5)

    def _click_finish(self):
        """
        点击完成
        """
        if self.d(text="完成").exists:
            self.d(text="完成").click()
        elif self.d(textContains="查看").exists:
            self.d(textContains="查看").click()
