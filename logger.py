import os
import glob
import time

class LogMonitor:
    def __init__(self, log_directory, callback, stop_event, check_interval=1):
        """
        初始化日志监控器
        :param log_directory: 日志文件夹路径
        :param callback: 新日志内容回调函数
        :param stop_event: 用于停止线程的事件标志
        :param check_interval: 检查间隔时间（秒）
        """
        self.log_directory = log_directory
        self.callback = callback
        self.stop_event = stop_event
        self.check_interval = check_interval
        self.start_time = None
        self.last_size = 0
        self.latest_log = None

    def find_latest_log_file(self):
        """
        查找指定目录下最新的日志文件，并确保文件的修改时间大于程序启动时间
        """
        print("looking for latest logfile")
        log_files = glob.glob(os.path.join(self.log_directory, 'script_*.log'))
        
        if not log_files:
            return None

        # 筛选出修改时间大于程序启动时间的日志文件
        valid_files = [
            log_file for log_file in log_files
            if os.path.getmtime(log_file) > self.start_time
        ]

        # 返回最新的日志文件
        return max(valid_files, key=os.path.getmtime) if valid_files else None

    def get_new_content(self, file_path):
        """
        获取文件从上次读取之后新增的内容
        """
        current_size = os.path.getsize(file_path)
        new_content = ""
        
        if current_size > self.last_size:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    file.seek(self.last_size)
                    new_content = file.read()
            except Exception as e:
                print(f"Error reading file: {e}")
        
        self.last_size = current_size
        return new_content

    def monitor(self):
        """
        开始监控日志文件更新
        """
        self.start_time = time.time()  # 记录程序的启动时间
        while not self.stop_event.is_set():
            # 检查是否已找到符合条件的日志文件
            if not self.latest_log:
                self.latest_log = self.find_latest_log_file()
                if not self.latest_log:
                    time.sleep(self.check_interval)
                    continue

            new_content = self.get_new_content(self.latest_log)
            if new_content:
                self.callback(new_content)

            time.sleep(self.check_interval)

        print("Log monitor stopped.")
