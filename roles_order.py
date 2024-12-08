import json

def sort_roles_by_team(input_file, output_file):
    # 指定排序的优先级
    team_order = {
        "townsfolk": 1,   # 镇民
        "outsider": 2,    # 外来者
        "minion": 3,      # 爪牙
        "demon": 4,       # 恶魔
        "fabled": 5        # 传奇角色
    }

    try:
        # 读取 JSON 文件
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 确保 JSON 数据是一个列表
        if not isinstance(data, list):
            raise ValueError("The JSON file should contain a list of roles.")

        # 按照 team_order 中的优先级排序
        sorted_data = sorted(
            data,
            key=lambda role: team_order.get(role.get("team", "").lower(), float('inf'))
        )

        # 保存排序后的数据到新文件
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(sorted_data, file, ensure_ascii=False, indent=4)

        print(f"Roles have been sorted by team and saved to {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # 输入 JSON 文件路径
    input_file = "src\\roles.json"  
    # 输出 JSON 文件路径
    output_file = "src\\roles.json" 

    # 调用排序函数
    sort_roles_by_team(input_file, output_file)
