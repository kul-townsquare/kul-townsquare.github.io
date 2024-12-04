import json
import argparse

def generate_script_summary(input_file):
    # 读取 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 初始化变量
    script_info = None
    roles = []

    # 遍历 JSON 数据
    for item in data:
        if "id" in item and item["id"] == "_meta":  # 检查是否是剧本元信息
            script_info = {
                "id": item.get("name", ""),
                "name": item.get("name", ""),
                "author": item.get("author", ""),
                "description": item.get("description", ""),
                "isOfficial": False,  # 假设所有剧本是非官方的
                "logo": item.get("logo", ""),
                "additional": item.get("additional", [])
            }
        elif "name" in item:  # 检查是否是角色信息
            roles.append(item)

    # 如果没有找到剧本元信息，抛出异常
    if script_info is None:
        raise ValueError("No script metadata found with `id` set to `_meta`.")

    # 将角色列表添加到剧本信息
    # script_info["roles"] = [role["name"] for role in roles]
    script_info["roles"] = [role["id"] for role in roles]

    return script_info, roles


def add_to_database(input_file, editions_file, roles_file):
    # 提取剧本信息和角色信息
    script_info, new_roles = generate_script_summary(input_file)

    # 读取 editions.json
    with open(editions_file, 'r+', encoding='utf-8') as editions_file_obj:
        editions = json.load(editions_file_obj)

        # 添加新剧本信息到 editions.json
        editions.append(script_info)

        # 保存更新的 editions.json
        editions_file_obj.seek(0)
        json.dump(editions, editions_file_obj, ensure_ascii=False, indent=4)
        editions_file_obj.truncate()

    print(f"Added new script '{script_info['name']}' to {editions_file}.")

    # 读取 roles.json
    with open(roles_file, 'r+', encoding='utf-8') as roles_file_obj:
        roles_data = json.load(roles_file_obj)
        existing_roles = {role['id'] for role in roles_data}

        # 找出需要添加的新角色
        roles_to_add = [role for role in new_roles if role["id"] not in existing_roles]
        print("New roles to add:", [role["name"] for role in roles_to_add])

        # 添加新角色到 roles.json
        # for role in roles_to_add:
        #     role["id"] = role["name"]
        roles_data.extend(roles_to_add)

        # 保存更新的 roles.json
        roles_file_obj.seek(0)
        json.dump(roles_data, roles_file_obj, ensure_ascii=False, indent=4)
        roles_file_obj.truncate()

    print(f"Added {len(roles_to_add)} new roles to {roles_file}.")

def main():
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Add a new script to the database and update roles.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON file for the new script.")
    parser.add_argument("--editions_file", default="src\editions.json", type=str, help="Path to the editions JSON file.")
    parser.add_argument("--roles_file", default="src\\roles.json", type=str, help="Path to the roles JSON file.")
    args = parser.parse_args()

    # 添加剧本到数据库
    add_to_database(args.input_file, args.editions_file, args.roles_file)


if __name__ == "__main__":
    main()
