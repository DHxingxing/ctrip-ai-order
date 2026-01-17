from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time

def run_appium_test():
    # 1. 配置启动参数
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "emulator-5554"
    
    # --- 这里填入你刚才获取到的信息 ---
    options.app_package = "ctrip.android.view.debug"
    options.app_activity = "ctrip.business.splash.CtripSplashActivity"
    # -------------------------------------
    
    options.app_wait_activity = "*"
    # no_reset=True 表示不清除 App 数据（如登录状态），方便测试
    # 如果想每次都像新安装一样启动，改为 False
    options.no_reset = True 
    
    # 2. 连接 Appium Server
    # 确保你的 Appium Server 正在运行 (默认端口 4723)
    appium_server_url = "http://127.0.0.1:4723"
    
    print(f"正在连接 Appium Server: {appium_server_url} ...")
    driver = None
    try:
        driver = webdriver.Remote(appium_server_url, options=options)
        print("✅ 连接成功！App 应该已经在模拟器上弹起了。")
        
        # 3. 这里可以开始写你的自动化逻辑
        # 比如打印当前的 Activity 确认是否跳转正确
        print(f"当前页面 Activity: {driver.current_activity}")

        # 简单的等待演示
        time.sleep(3)

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("请检查：\n1. Appium Server 是否已启动？\n2. 模拟器是否在线？\n3. 包名是否正确？")
    
    finally:
        if driver:
            driver.quit()
            print("连接已关闭。")

if __name__ == "__main__":
    run_appium_test()