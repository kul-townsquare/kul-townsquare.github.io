import json

def update_json_ids(file_path):
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 遍历数据并修改 `id`
    for item in data:
        if 'name' in item and 'id' in item:
            item['id'] = item['name']  # 将 `id` 设置为 `name`

    # 将修改后的数据写回 JSON 文件
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Updated `id` for all items in {file_path}.")

# 替换为你的 JSON 文件路径
file_path = 'src/roles.json'
update_json_ids(file_path)
