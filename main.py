import uiautomator2 as u2
import time
import select_city
import select_time
from dynamic_xml_locator import DynamicXmlLocator
from smart_filter import SmartFilter
# ==========================================
# 核心设置区域
# ==========================================
TARGET_CITY = "sanya"  # 你想去的城市
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
def main():
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
        
        # 步骤 4: 点击首页查询按钮，进入列表页
        print("🤖 正在寻找首页【查询】按钮...")
        # 实例化定位器
        locator = DynamicXmlLocator(d)
        
        # 优先使用用户指定的 ID (兼容 resource-id 和 content-desc)
        home_search_id = "car_testid_page_home_search_btn"
        
        if d(resourceId=home_search_id).exists:
             d(resourceId=home_search_id).click()
             print(f"👉 点击查询按钮 (ID: {home_search_id})")
        elif d(description=home_search_id).exists:
             d(description=home_search_id).click()
             print(f"👉 点击查询按钮 (Desc: {home_search_id})")
        else:
             # 动态查找兜底
             query_btn_id = locator.find_id_by_text("查询") or locator.find_id_by_text("搜索")
             if query_btn_id:
                 d(resourceId=query_btn_id).click()
                 print(f"👉 动态点击查询按钮 (ID: {query_btn_id})")
             else:
                 d(textContains="查询").click()
                 print("👉 点击文字【查询】")

        # 等待列表页加载
        print("⏳ 等待列表页加载...")
        time.sleep(5)

        # 步骤 5: (新) 智能筛选车辆
        # 假设我们想要选这些条件（你可以随时改）
        my_filters = ["送车上门", "自助取还", "不限里程", "积分当钱花", "身份证","星月租车"]
        
        print(f"🔎 进入列表页，准备进行筛选: {my_filters}")
        filter_bot = SmartFilter(d)
        filter_bot.select_options(my_filters)
        
        print("✅ 流程结束")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        d.screenshot("error.jpg")

    finally:
            # ===========================================
            # 🧹 清理战场：无论上面发生什么，这里都会执行
            # ===========================================
            print(f"正在强制关闭 App: {PACKAGE_NAME} ...")
            d.app_stop(PACKAGE_NAME)
            print("App 已关闭，手机桌面已清理。")

if __name__ == "__main__":
    main()