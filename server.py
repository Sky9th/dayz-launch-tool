import os
import subprocess
from read_config import read_config  # 导入 read_config.py 中的函数

# 调用 read_config 函数读取配置
config = read_config()
               
subprocess.run([
    os.path.join(config['dayZInstallPath'], "DayZDiag_x64.exe"),  # 执行的程序
    config['modParams'],  # mod 参数，应该是多个 mod 目录拼接成的字符串
    "-filePatching",  # 额外的命令行参数
    "-server",  # 额外的命令行参数
    "-config", os.path.join(config['dayZInstallPath'], "serverDZ.cfg")  # 指定任务
])