import uiautomator2 as u2
import time
import datetime

# ==========================================
# 1. 日期计算函数 (保持不变)
# ==========================================
def get_target_dates():
    """
    计算【明天】(取车) 和【后天】(还车) 的日期数字
    例如：今天是1月31日 -> 返回 ("1", "2")
    """
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    day_after = now + datetime.timedelta(days=3) # 租2天
    
    # 核心细节：去掉日期的前导0 (比如 "05" -> "5")
    pickup = str(int(tomorrow.strftime("%d")))
    dropoff = str(int(day_after.strftime("%d")))
    
    return pickup, dropoff

# ==========================================
# 2. 核心点击函数 (已修改为：坐标中心点击法)
# ==========================================
def click_calendar_date(d, date_text, action_name="日期"):
    """
    智能点击日历日期 - 方案一：坐标暴力点击
    :param d: u2 设备对象
    :param date_text: 日期数字 (如 "19")
    """
    print(f"👉 正在寻找【{action_name}】: {date_text}号")
    
    # 查找条件：只要文本匹配就行 (去掉了 className 限制，兼容性更强)
    selector = d(text=date_text)
    
    # --- 内部函数：执行坐标点击 ---
    def execute_coordinate_click(element):
        try:
            # 1. 获取元素的坐标范围 (bounds)
            # 格式: {'left': 100, 'top': 200, 'right': 150, 'bottom': 250}
            bounds = element.info['bounds']
            
            # 2. 计算中心点坐标
            center_x = (bounds['left'] + bounds['right']) / 2
            center_y = (bounds['top'] + bounds['bottom']) / 2
            
            print(f"📍 找到数字，坐标范围: {bounds}")
            print(f"👆 忽略层级，直接点击中心坐标: ({center_x}, {center_y})")
            
            # 3. 执行物理点击
            d.click(center_x, center_y)
            return True
        except Exception as e:
            print(f"⚠️ 坐标计算或点击失败: {e}")
            return False

    # --- 策略 1: 当前屏幕直接找 ---
    if selector.exists:
        # 直接调用坐标点击
        if execute_coordinate_click(selector):
            return True
            
    # --- 策略 2: 滑动查找 (处理跨月) ---
    print(f"⚠️ 当前页未看到 {date_text}号，尝试向上滑动日历...")
    
    # 向下滑动：手指从 0.8 拖到 0.5
    d.swipe(0.5, 0.8, 0.5, 0.5, duration=0.3)
    time.sleep(1.0) # 等待滑动结束
    
    # 滑动后再找一次
    if selector.exists:
        if execute_coordinate_click(selector):
            print(f"✅ 滑动后点击 {date_text} 成功")
            return True
        
    print(f"❌ 彻底没找到日期 {date_text}，可能逻辑有误")
    return False

# ==========================================
# 3. 完整流程封装 (保持不变)
# ==========================================
def select_dates_flow(d):
    """
    执行完整的选日期流程
    """
    print("--- 🕒 启动选日期流程 ---")
    
    timeline_id = "car_testid_page_list_search_pannel_timeline"
    if d(resourceId=timeline_id).exists:
        d(resourceId=timeline_id).click()
        print("点击时间栏，进入日历...")
    else:
        print("⚠️ 未找到时间栏 ID，尝试点击 '取车' 文字区域")
        d(textContains="取车").click()

    time.sleep(2) # 等待日历加载

    # 计算日期
    pickup_day, dropoff_day = get_target_dates()
    print(f"📅 计划操作: 取车[{pickup_day}号] -> 还车[{dropoff_day}号]")
    
    # 点击取车
    click_calendar_date(d, pickup_day, "取车")
    time.sleep(1.0) 
    
    # 点击还车
    click_calendar_date(d, dropoff_day, "还车")
    time.sleep(1.0)
    
    # 点击确定
    print("准备点击【确定】...")
    if d(text="确定").exists:
        d(text="确定").click()
        print("✅ 点击文字版【确定】")
    else:
        print("⚠️ 未找到确定按钮文字，使用坐标盲点右下角")
        w, h = d.window_size()
        d.click(w * 0.85, h * 0.95)
