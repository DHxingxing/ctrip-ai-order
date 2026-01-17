import uiautomator2 as u2
import time
import select_city
# ==========================================
# 核心设置区域
# ==========================================
TARGET_CITY = "shanghai"  # 你想去的城市
PACKAGE_NAME = "ctrip.android.view.debug" # 携程的包名 (请确保和你手机里的一致)

# ==========================================
# 1. 连接手机与初始化
# ==========================================
d = u2.connect() 

print(f"正在启动携程 App ({PACKAGE_NAME})...")
d.app_start(PACKAGE_NAME)
time.sleep(5) 

# ==========================================
# 功能函数封装
# ==========================================

# ==========================================
# 主执行流程
# ==========================================

try:
    # 步骤 1: 点击首页的“租车自驾”
    rental_btn_id = "ctrip.android.view.debug:id/home_grid_car_widget"
    
    print("正在寻找【租车自驾】入口...")
    if d(resourceId=rental_btn_id).exists(timeout=10):
        d(resourceId=rental_btn_id).click()
        print("点击成功，进入租车首页。")
    else:
        print("ID 未找到，尝试点击文字【租车自驾】...")
        d(text="租车自驾").click()

    time.sleep(3) # 稍微多等一秒，防止页面加载慢

    # 步骤 2: 点击左上角的“取车城市”
    pickup_city_btn_id = "car_testid_page_home_pickup_city"
    
    print("正在点击取车城市区域...")
    # 这里加个判断更稳
    if d(resourceId=pickup_city_btn_id).exists(timeout=5):
        d(resourceId=pickup_city_btn_id).click()
    else:
        # 如果还没加载出来，可能是还没跳转完
        print("警告：没找到城市选择按钮，尝试直接点文字...")
        d(textContains="取车").click()
    
    time.sleep(1.5) # 等选择页弹出

    # 步骤 3: 调用滑动查找函数 (这里名字改对了)
    select_city.search_city_by_paste(TARGET_CITY, d)
    
    print("🎉 流程结束：城市选择完毕！")

except Exception as e:
    print(f"❌ 发生错误: {e}")
    d.screenshot("error.jpg")