import json

def clear_images_from_roles(roles_file):
    # 读取 roles.json 文件
    try:
        with open(roles_file, 'r', encoding='utf-8') as file:
            roles = json.load(file)
    except FileNotFoundError:
        print(f"Error: File {roles_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: File {roles_file} is not a valid JSON.")
        return

    # 清除每个角色的 image 字段
    for role in roles:
        if "image" in role:
            role["image"] = ""  # 清空 image 字段

    # 写回 roles.json 文件
    try:
        with open(roles_file, 'w', encoding='utf-8') as file:
            json.dump(roles, file, ensure_ascii=False, indent=4)
        print(f"Successfully cleared all image fields in {roles_file}.")
    except IOError as e:
        print(f"Error writing to file {roles_file}: {e}")

if __name__ == "__main__":
    # 输入 roles.json 文件路径
    roles_file = "src\\roles.json"  # 替换为你的 roles.json 文件路径

    # 调用清除函数
    clear_images_from_roles(roles_file)
