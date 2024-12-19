import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogHandler(FileSystemEventHandler):
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.last_size = {}  # 存储每个文件的上次读取大小
        self.client_file = None  # 当前客户端日志文件
        self.server_file = None  # 当前服务器日志文件

    def on_modified(self, event):
        """监听文件变化，更新当前监控文件"""
        if event.is_directory:
            return
        elif event.src_path.endswith(".log"):  # 客户端日志
            self.check_and_replace_file(event.src_path, "client")
        elif event.src_path.endswith(".RPT"):  # 服务器日志
            self.check_and_replace_file(event.src_path, "server")

    def check_and_replace_file(self, file_path, file_type):
        """检查文件是否是新的文件并替换当前文件"""
        if file_type == "client":
            if self.client_file is None or file_path > self.client_file:
                self.client_file = file_path
        elif file_type == "server":
            if self.server_file is None or file_path > self.server_file:
                self.server_file = file_path

    def process_log(self):
        """检查当前客户端和服务器日志文件的新增内容"""
        try:
            # 处理客户端文件
            if self.client_file:
                self.check_file_for_new_content(self.client_file, "client")
            # 处理服务器文件
            if self.server_file:
                self.check_file_for_new_content(self.server_file, "server")
        except Exception as e:
            print(f"Error reading log files: {e}")

    def check_file_for_new_content(self, file_path, log_type):
        """检查指定文件是否有新增内容"""
        current_size = os.path.getsize(file_path)
        if file_path not in self.last_size:
            # 如果是新文件，初始化文件大小
            self.last_size[file_path] = current_size
            return  # 跳过第一次读取

        last_size = self.last_size[file_path]

        # 如果文件大小增加，说明有新内容
        if current_size > last_size:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(last_size)  # 从上次读取的位置继续读取
                new_content = f.read()  # 读取新增的部分
                self.last_size[file_path] = current_size  # 更新文件大小
                self.log_callback(log_type, new_content)

    def determine_log_type(self, file_path):
        """根据文件名判断日志类型"""
        if re.search(r"script_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.log", file_path):
            return "client"
        elif re.search(r"DayZServer_x64_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.RPT", file_path):
            return "server"
        return "unknown"


def monitor_script_logs(log_dir, log_callback):
    event_handler = LogHandler(log_callback)
    observer = Observer()
    observer.schedule(event_handler, log_dir, recursive=False)
    observer.start()

    try:
        while True:
            print("Scanning logs...")
            event_handler.process_log()  # 每秒检查当前文件的新增内容
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# # 示例回调函数
# def log_handler(log_type, content):
#     print(f"[{log_type.upper()} LOGS]\n{content}")

# # 调用监控函数
# monitor_script_logs(r"C:\Users\Sky9th\AppData\Local\DayZ", log_handler)
