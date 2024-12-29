import subprocess
import os
from PySide6.QtCore import QThread, Signal
from read_config import read_config
import time


# 打包线程
class DayZRunThread(QThread):

    run_signal = Signal()  # row index, status update signal

    def __init__(self, dayzMode, program, server, config):
        super().__init__()
        self.dayzMode = dayzMode
        self.program = program
        self.server = server
        self.config = config

    def run(self):
        # 调用 read_config 函数读取配置
        """
        运行 DayZ 并实时捕获其输出。
        
        :param log_callback: 可选的回调函数，用于处理实时日志输出
        """           
        if (self.server):
            path = self.config["dayZServerInstallPath"]
            exe = "DayZServer_x64.exe"
        else:
            if (self.program == "DayZ"):
                path = self.config["dayZInstallPath"]
                exe = "DayZ_BE.exe"
            elif (self.program == "DayZDiag Offline"):
                path = self.config["dayZInstallPath"]
                exe = "DayZDiag_x64.exe"

        
        # 构建命令
        if self.server:
            command = [
                os.path.join(path, exe),
                self.config['modParams'],  # mod 参数，应该是多个 mod 目录拼接成的字符串
                "-filePatching",  # 额外的命令行参数
                "-server",  # 额外的命令行参数
                "-dologs",
                "-debug",
                "-profiles=ServerDebugProfile",
                "-config", os.path.join(path, "serverDZ.cfg")  # 指定任务
            ]
        else:
            command = [
                os.path.join(path, exe),
                self.config['modParams'],  # 分割 mod 参数字符串
                "-profiles=ClientDebugProfile",
                "-d",
                "-dologs",
                "-debug",
                "-filePatching"  # 确保将 "-filePatching" 添加到命令行参数中
            ]

            if (self.program == "DayZDiag Offline"):
                    command.append("-mission")
                    command.append(self.config["offlineMissoinPath"])
                    
            if (self.dayzMode == "AutoConnect"):
                    command.append("-connect=")
                    command.append("127.0.0.1:2302")

        print(command)

        # 运行子进程
        subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.run_signal.emit()


# q = PackThread(read_config())
# q.run()