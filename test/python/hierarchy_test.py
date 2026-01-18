import uiautomator2 as u2
import time

def select_general_options(d, target_keywords):
    """
    万能筛选器：自动处理 租车公司、取还方式、价格 等所有选项
    原理：利用 car_testid_comp_filter_modal_item_ 通用前缀
    """
    print(f"\n--- 🛡️ 启动通用筛选，目标: {target_keywords} ---")

    # 1. 【核心修改】正则升级
    # 之前是 ".*item_Vendor.*" (只找供应商)
    # 现在改用 "car_testid_comp_filter_modal_item_.*" (匹配所有筛选格子)
    # 这样就能同时抓到 Price, SelfService, Vendor 等所有选项
    print("👀 正在扫描所有筛选选项 (过滤掉纯标题)...")
    
    # 匹配所有 ID 以 car_testid_comp_filter_modal_item_ 开头的元素
    all_options = d(resourceIdMatches="car_testid_comp_filter_modal_item_.*")

    try:
        count = len(all_options)
        print(f"📊 当前屏幕共识别到 {count} 个可点击选项")
    except:
        print("⚠️ 获取元素失败，请检查连接")
        return

    found_count = 0
    
    # 2. 遍历所有找到的“格子”
    for i, item in enumerate(all_options):
        try:
            # 在格子（ViewGroup）里找文字（TextView）
            child_text = item.child(className="android.widget.TextView")
            
            if child_text.exists:
                text_content = child_text.info['text']
                
                # print(f"   [{i}] 扫描: {text_content}") # 调试用，平时可注释

                # 3. 匹配逻辑
                # 检查这个格子的文字，是否包含在我们的目标列表中
                is_match = False
                matched_kw = ""
                
                for kw in target_keywords:
                    # 使用 in 进行模糊匹配，比如 "50" 可以匹配 "¥50以下"
                    # 如果需要精确匹配，可以用 if kw == text_content
                    if kw in text_content:
                        is_match = True
                        matched_kw = kw
                        break
                
                if is_match:
                    print(f"✅ 找到目标: 【{text_content}】 (匹配关键词: {matched_kw})")
                    
                    # 4. 坐标点击 (解决 clickable=false)
                    bounds = item.info['bounds']
                    cx = (bounds['left'] + bounds['right']) / 2
                    cy = (bounds['top'] + bounds['bottom']) / 2
                    
                    # 只有当元素在屏幕内部才点击 (防止点到屏幕外面报错)
                    # 简单判断一下 y 坐标
                    screen_h = d.window_size()[1]
                    if 0 < cy < screen_h:
                        print(f"👆 点击坐标: ({cx}, {cy})")
                        d.click(cx, cy)
                        found_count += 1
                        time.sleep(0.5) # 点完稍微等一下
                    else:
                        print("⚠️ 元素在屏幕外，可能需要滑动")
                        
        except Exception as e:
            # 某些特殊情况可能没有 child，忽略
            pass

    if found_count == 0:
        print("⚠️ 当前屏未找到目标，请检查关键词或尝试滑动屏幕。")
    else:
        print(f"🎉 已完成 {found_count} 个选项的选择。")

# ================= 测试入口 =================
if __name__ == '__main__':
    d = u2.connect()
    
    # 你可以把所有想选的混在一起传进去
    # 比如：一个价格，一个取还方式，一个租车公司
    my_targets = [
        "送车上门",    # 会匹配到 item_SelfService
        "不限里程",     # 会匹配到 item_Price
        "非自助取还",  # 也会匹配到
        "身份证"     # 会匹配到 item_Vendor
    ]
    
    select_general_options(d, my_targets)