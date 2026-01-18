import uiautomator2 as u2

d = u2.connect()

# 获取当前的页面结构 (XML格式)
xml_content = d.dump_hierarchy()

# 1. 获取当前APP的信息（字典格式）
current_app = d.app_current()
# 提取包名和活动名，作为文件名的一部分
package_name = current_app.get("package", "unknown_package")
activity_name = current_app.get("activity", "unknown_activity")

# 2. 处理文件名：替换特殊字符，避免路径非法
# 把/、:、.等特殊字符替换为下划线
safe_activity = activity_name.replace("/", "_").replace(":", "_").replace(".", "_")
# 拼接合法的文件名（格式：包名_活动名_page_hierarchy.xml）
file_name = f"{package_name}_{safe_activity}_page_hierarchy.xml"

# 3. 保存文件（默认保存到当前运行目录，也可指定绝对路径）
# 如需指定目录：save_path = os.path.join("指定目录路径", file_name)
save_path = file_name
with open(save_path, "w", encoding="utf-8") as f:
    f.write(xml_content)

print("✅ 控件树已保存到 page_hierarchy.xml")