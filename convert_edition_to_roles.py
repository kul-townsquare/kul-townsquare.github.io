import json
import argparse

def generate_script_summary(input_file, output_file):
    # 读取 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 初始化变量
    script_info = None
    roles = set()

    # 遍历 JSON 数据
    for item in data:
        if "id" in item and item["id"] == "_meta":  # 检查是否是剧本元信息
            script_info = {
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "author": item.get("author", ""),
                "description": item.get("description", ""),
                "isOfficial": False,  # 假设所有剧本是非官方的
                "logo": item.get("logo", ""),
                "additional": item.get("additional", [])
            }
        if "name" in item:  # 检查是否包含角色
            roles.add(item["name"])

    # 如果没有找到剧本元信息，抛出异常
    if script_info is None:
        raise ValueError("No script metadata found with `id` set to `_meta`.")

    # 将角色列表添加到剧本信息
    script_info["roles"] = list(roles)

    # 保存到新的 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(script_info, file, ensure_ascii=False, indent=4)

    print(f"Script summary has been saved to {output_file}.")

    # 转换为 JSON 字符串
    return json.dumps(script_info, ensure_ascii=False, indent=4)


def main():
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Generate a script summary from a JSON file.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON file.")
    parser.add_argument("--output_file", default="output_file.json", type=str, help="Path to the output JSON file.")
    args = parser.parse_args()

    # 调用生成函数
    result = generate_script_summary(args.input_file, args.output_file)

    # 打印结果
    print(result)


if __name__ == "__main__":
    main()
