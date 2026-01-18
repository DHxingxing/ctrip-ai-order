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
            self._process_current_screen(target_keywords)
            
            # 检查是否全部完成
            # 注意：有些关键词可能本来就不存在，所以不能强求 len相等 才退出
            # 这里我们还是坚持滑到底，除非已经全找到了
            if len(self.processed_keywords) >= len(target_keywords):
                print("🎉 所有目标都已找到并点击！")
                break
            
            # 滑动翻页
            # 到底检测：如果滑不动了或者页面没变，就停止
            # 简单起见，我们先按固定次数滑，或者检查底部文字
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
        """
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
