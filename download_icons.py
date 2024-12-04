import os
import json
import requests

def download_images_from_roles(roles_file, output_dir):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 读取 roles.json 文件
    with open(roles_file, 'r', encoding='utf-8') as file:
        roles = json.load(file)

    for role in roles:
        role_id = role.get("id")
        role_name = role.get("name")
        image_url = role.get("image")

        # 拼接本地文件路径
        output_file = os.path.join(output_dir, f"{role_id}.png")

        # 检查是否已经存在文件
        if os.path.exists(output_file):
            print(f"Skipping: {role_id}, file already exists.")
            continue

        # 检查是否是 HTTPS 链接
        if image_url and image_url.startswith("https://"):
            # 拼接文件路径
            output_file = os.path.join(output_dir, f"{role_id}.png")

            # 下载图片
            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()  # 检查请求是否成功

                # 保存图片
                with open(output_file, "wb") as img_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        img_file.write(chunk)

                print(f"Downloaded: {role_name} -> {output_file}")
            except requests.RequestException as e:
                print(f"Failed to download {image_url}: {e}")
        else:
            print(f"Skipping: {role_name}, invalid or missing image URL.")

if __name__ == "__main__":
    # 输入 roles.json 文件路径
    roles_file = "src/roles.json"  # 替换为你的 roles.json 文件路径
    # 输出图片目录
    output_dir = "src/assets/icons"  # 替换为你的目标文件夹路径

    # 调用下载函数
    download_images_from_roles(roles_file, output_dir)
