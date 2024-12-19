import os
import subprocess
import sys

from util import get_resource_path


def read_config(config_file="./config.txt"):
    """
    读取配置文件并返回配置字典。
    """

    config_file = get_resource_path("config.txt")
    # 初始化配置字典
    config = {
        "mountDriverPath": "",
        "dayZInstallPath": "",
        "dayZServerInstallPath": "",
        "devMod": "",
        "dependeciesMod": "",
        "missionPath": "",
        "offlineMissoinPath": "",
        "workbenchPath": "",
        "modParams": []
    }

    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f"Configuration file {config_file} not found!")
        exit(1)

    # 读取配置文件
    with open(config_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key in config:
                    config[key] = value

    # 设置 mod 参数列表
    mod_params = []
    print(config)

    def find_config_cpp(base_path, mount_path):
        """
        遍历指定路径下所有包含 config.cpp 文件的目录或以 @ 开头的文件夹，
        并将它们加入 mod_params。同时同步将路径创建软链接到 mountDriverPath 和 dayZInstallPath。
        """
        if os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path):
                # 条件：包含 config.cpp 或当前文件夹名以 @ 开头
                if "config.cpp" in files or os.path.basename(root).startswith("@"):
                    folder_path = root  # 当前文件夹路径
                    relative_path = os.path.relpath(folder_path, base_path)  # 计算相对路径
                    
                    # 构建软链接目标路径
                    mount_link_path = os.path.join(mount_path, relative_path)
                    dayz_link_path = os.path.join(config["dayZInstallPath"], relative_path)

                    # 添加到 mod_params
                    mod_params.append(f"{mount_path}{relative_path}")

                    # 创建软链接
                    create_symlink(folder_path, mount_link_path)
                    create_symlink(folder_path, dayz_link_path)

    def create_symlink(source, target):
        """
        创建软链接（Windows mklink /D）。
        如果目标路径已存在且为文件，则抛出错误；如果是目录则跳过。
        """
        if os.path.exists(target):
            if os.path.isfile(target):  # 如果路径是文件，报错
                raise FileExistsError(f"Target path exists as a file: {target}")
            elif os.path.isdir(target):  # 如果路径已存在且是目录，跳过
                print(f"Directory already exists, skipping: {target}")
                return
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)  # 确保目标父目录存在

        try:
            subprocess.run(f'mklink /D "{target}" "{source}"', shell=True, check=True)
            print(f"Link created: {target} -> {source}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create link: {e}")

    # 遍历 dependeciesMod 目录
    find_config_cpp(config["dependeciesMod"], config["mountDriverPath"])

    # 遍历 devMod 目录
    find_config_cpp(config["devMod"], config["mountDriverPath"])

    # 设置最终的 modParams
    if mod_params:
        config["modParams"] = "-mod=" + ";".join(mod_params)

    # 输出时处理路径的斜杠
    for key in config:
        if isinstance(config[key], str):
            config[key] = config[key].replace("/", "\\")
        elif isinstance(config[key], list):
            config[key] = [item.replace("/", "\\") for item in config[key]]

    return config