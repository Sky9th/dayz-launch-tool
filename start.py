import os
import subprocess
from read_config import read_config  # 导入 read_config.py 中的函数

# 调用 read_config 函数读取配置
config = read_config()

# 启动 DayZ 带 mod 和 mission
subprocess.run([os.path.join(config['dayZInstallPath'], "DayZ_x64.exe"), config['modParams'], "-filePatching"])
