import os
import subprocess
from read_config import read_config  # 导入 read_config.py 中的函数


def run(dayzMode, program, server):
    # 调用 read_config 函数读取配置
    """
    运行 DayZ 并实时捕获其输出。
    
    :param log_callback: 可选的回调函数，用于处理实时日志输出
    """

    config = read_config()
    if (program == "DayZ"):
        if (server):
            path = config["dayZServerInstallPath"]
            exe = "DayZServer_x64.exe"
        else:
            path = config["dayZInstallPath"]
            exe = "DayZ_x64.exe"
    elif (program == "Workbench"):
        path = config["workbenchPath"]
        exe = "workbenchApp.exe"
    else:
        if (server):
            path = config["dayZInstallPath"]
            exe = "DayZDiag_x64.exe"
        else:
            path = config["dayZInstallPath"]
            exe = "DayZDiag_x64.exe"     
    
    # 构建命令
    if server:
        command = [
            os.path.join(path, exe),
            config['modParams'],  # mod 参数，应该是多个 mod 目录拼接成的字符串
            "-filePatching",  # 额外的命令行参数
            "-server",  # 额外的命令行参数
            "-profiles=ServerProfile",
            "-config", os.path.join(path, "serverDZ.cfg")  # 指定任务
        ]
    else:
        command = [
            os.path.join(path, exe),
            config['modParams'],  # 分割 mod 参数字符串
            "-profiles=ClientProfile",
            "-d",
            "-filePatching"  # 确保将 "-filePatching" 添加到命令行参数中
        ]

        
    if (dayzMode == "mission"):
        if(server and exe == "DayZDiag_x64.exe"):
            command.append("-mission")
            command.append(config["offlineMissoinPath"])
        elif(server == False):
            command.append("-mission")
            command.append(config["offlineMissoinPath"])

    print(command)

    # 运行子进程
    subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
