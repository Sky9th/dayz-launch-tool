import subprocess
import os
from PySide6.QtCore import QThread, Signal
from read_config import read_config


# 打包线程
class PackThread(QThread):

    progress_signal = Signal(str, str)  # row index, status update signal
    pack_signal = Signal(str)

    def __init__(self, config, kill):
        super().__init__()
        self.config = config
        self.kill = kill
        self.target = self.config["mountDriverPath"]
        self.source = self.config["devMod"]

    def run(self):
        
        for folder in os.listdir(self.source):
            folder_path = os.path.join(self.source, folder)
            if os.path.isdir(folder_path) and folder.startswith(".") == False:
                self.progress_signal.emit(folder, "Pending")  

        modPath = self.target + "@" + self.config["devModName"]
        addPath = modPath + "\\addons"
        makePbo = self.config["MikeroDePboToolsMakePboPath"] + "\\DePboTools\\bin\\MakePbo.exe"

        packed_folders = [];
        folder_sizes = self.load_folder_sizes(self.config["folderSize"])
        for folder in os.listdir(self.source):
            folder_path = os.path.join(self.source, folder)
            if os.path.isdir(folder_path) and folder.startswith(".") == False:
                if(folder in folder_sizes):
                    if(self.get_folder_size(folder) != folder_sizes[folder]):
                        packed_folders.append(folder)
                        continue
                else:
                    packed_folders.append(folder)      
                    continue
            
            self.progress_signal.emit(folder, "Done")  

        # 检查并创建目标文件夹
        if not os.path.exists(modPath):
            os.makedirs(modPath)
        if not os.path.exists(addPath):
            os.makedirs(addPath)

        packed = True

        if (len(packed_folders) > 0 and self.kill):
            self.kill()

        # 获取 source 目录下所有的文件夹
        for folder in packed_folders:
            folder_path = os.path.join(self.source, folder)
            # 确保是文件夹
            if os.path.isdir(folder_path) and folder.startswith(".") == False:
                # 打包文件夹为 PBO 文件
                pbo_filename = os.path.join(addPath, folder + ".pbo")
                # command = f'"{makePbo}" "P:\\{folder}" "{pbo_filename}"'
                command = [makePbo, "-P", f"P:\\{folder}", f"{pbo_filename}"];
                print(command)
                try:
                    process = subprocess.Popen(command, shell=True)
                    process.wait()
                    print(f"Successfully packed {folder} into {pbo_filename}")
                    if process.returncode == 0:
                        self.progress_signal.emit(folder, "Done")
                    else:
                        packed = False
                        self.progress_signal.emit(folder, "Failed")
                except Exception as e:
                    packed = False
                    self.progress_signal.emit(folder, f"Failed: {e}")
        
        if (packed):
            folder_sizes = self.get_folder_sizes(os.listdir(self.source))
            self.pack_signal.emit(folder_sizes)
        else:
            self.pack_signal.emit("")
            
        
    def get_folder_size(self, folder):
        total_size = 0
        folder_path = os.path.join(self.source, folder)
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
    
    def get_folder_sizes(self, folders):
        folder_sizes = []
        for folder in folders:
            folder_path = os.path.join(self.source, folder)
            if os.path.isdir(folder_path) and folder.startswith(".") == False:
                size = self.get_folder_size(folder_path)
                folder_sizes.append(f"{folder},{size}")
        return ";".join(folder_sizes);

    def load_folder_sizes(self, sizes):
        folder_sizes = {}
        if sizes:
            entries = sizes.split(";")
            for entry in entries:
                folder, size = entry.split(",")
                folder_sizes[folder] = int(size)
        return folder_sizes
    

# q = PackThread(read_config(), None)
# q.run()
