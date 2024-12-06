import os
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
        raise ValueError(f"No script metadata found in file: {input_file}")

    # 将角色列表添加到剧本信息
    script_info["roles"] = [role["id"] for role in roles]

    return script_info, roles


def add_to_database(input_file, editions_file, roles_file):
    # 提取剧本信息和角色信息
    script_info, new_roles = generate_script_summary(input_file)

    # 读取 editions.json
    with open(editions_file, 'r+', encoding='utf-8') as editions_file_obj:
        editions = json.load(editions_file_obj)

        # 检查是否已存在剧本
        if any(edition["name"] == script_info["name"] for edition in editions):
            print(f"Script '{script_info['name']}' already exists in {editions_file}. Skipping.")
            return

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
        roles_data.extend(roles_to_add)

        # 保存更新的 roles.json
        roles_file_obj.seek(0)
        json.dump(roles_data, roles_file_obj, ensure_ascii=False, indent=4)
        roles_file_obj.truncate()

    print(f"Added {len(roles_to_add)} new roles to {roles_file}.")


def process_folder(folder_path, editions_file, roles_file):
    # 遍历文件夹中的所有子文件夹
    for root, _, files in os.walk(folder_path):
        for file in files:
            # 处理 .json 文件
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    add_to_database(file_path, editions_file, roles_file)
                except ValueError as e:
                    print(f"Skipping {file_path}: {e}")


def main():
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Add new scripts to the database and update roles.")
    parser.add_argument("input_path", type=str, help="Path to the input file or folder containing scripts.")
    parser.add_argument("--editions_file", default="src/editions.json", type=str, help="Path to the editions JSON file.")
    parser.add_argument("--roles_file", default="src/roles.json", type=str, help="Path to the roles JSON file.")
    args = parser.parse_args()

    # 判断输入路径是文件还是文件夹
    if os.path.isfile(args.input_path):
        # 单个文件
        add_to_database(args.input_path, args.editions_file, args.roles_file)
    elif os.path.isdir(args.input_path):
        # 文件夹
        process_folder(args.input_path, args.editions_file, args.roles_file)
    else:
        print(f"Error: {args.input_path} is neither a file nor a folder.")


if __name__ == "__main__":
    main()
