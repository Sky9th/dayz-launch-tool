import os
import subprocess

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
        "MikeroDePboToolsMakePboPath": "",
        "devMod": "",
        "devModName": "",
        "dependeciesMod": "",
        "missionPath": "",
        "offlineMissoinPath": "",
        "workbenchPath": "",
        "selected": "",
        "kill_before_start": "",
        "folderSize": "",
        "modParams": [],
        "depend_mods": [],
        "dev_mods": [],
        "selected_mods": []
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
                    if (key == "selected"):
                        config["selected_mods"] = value.split(',')
                    elif (key == "selected_mods"):
                        continue
                    else:
                        config[key] = value

    # 设置 mod 参数列表
    mod_params = []
    depend_mods = []
    dev_mods = []
    # print(config)

    def find_mod_dir(base_path, mount_path, dev = True):
        """
        遍历指定路径下所有包含 config.cpp 文件的目录或以 @ 开头的文件夹，
        并将它们加入 mod_params。同时同步将路径创建软链接到 mountDriverPath 和 dayZInstallPath。
        """
        if os.path.exists(base_path):
            for folder in os.listdir(base_path):
                if folder.startswith(".") or os.path.isfile(base_path + "\\" + folder):
                    continue

                # 构建软链接目标路径
                mount_link_path = os.path.join(mount_path, folder)
                # dayz_link_path = os.path.join(config["dayZInstallPath"], relative_path)

                # 添加到 mod_params
                if folder.startswith("@"):
                    depend_mods.append(folder)
                    if folder in config["selected_mods"]:
                        mod_params.append(f"{mount_path}{folder}")
                elif dev:
                    if folder not in dev_mods:
                        dev_mods.append(folder)
                

                if(os.path.exists(mount_link_path) == False):
                    # 创建软链接
                    create_symlink(base_path + "\\" + folder, mount_link_path)
                    # create_symlink(folder_path, dayz_link_path)

    def create_symlink(source, target):
        """
        创建软链接（Windows mklink /D）。
        如果目标路径已存在且为文件，则抛出错误；如果是目录则跳过。
        """
        if os.path.exists(target):
            if os.path.isfile(target):  # 如果路径是文件，报错
                raise FileExistsError(f"Target path exists as a file: {target}")
            elif os.path.isdir(target):  # 如果路径已存在且是目录，跳过
                # print(f"Directory already exists, skipping: {target}")
                return
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)  # 确保目标父目录存在
            

        try:
            subprocess.run(f'mklink /D "{target}" "{source}"', shell=True, check=True)
            print(f"Link created: {target} -> {source}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create link: {e}")
    
    try:
        # 遍历 dependeciesMod 目录
        find_mod_dir(config["dependeciesMod"], config["mountDriverPath"], False)

        # 遍历 devMod 目录
        find_mod_dir(config["devMod"], config["mountDriverPath"])

    except subprocess.CalledProcessError as e:
        print(f"Error packing : {e}")
        pass
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        pass

    # 设置最终的 modParams
    if mod_params:
        config["modParams"] = "-mod=" + ";".join(mod_params) + ";" + config["mountDriverPath"] + "@" + config["devModName"]
    config["depend_mods"] = depend_mods
    config["dev_mods"] = dev_mods

    # 输出时处理路径的斜杠
    for key in config:
        if isinstance(config[key], str):
            config[key] = config[key].replace("/", "\\")
        elif isinstance(config[key], list):
            config[key] = [item.replace("/", "\\") for item in config[key]]

    return config