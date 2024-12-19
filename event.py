import os
import sys

import psutil
from run import run
from thread import Worker
from logger import monitor_script_logs  # 导入 logger 的监控日志函数
import traceback

from util import get_resource_path

def catch_exceptions(update_error_log):
    """
    A decorator to catch exceptions for instance methods and pass them to the error logging function.
    :param update_error_log: A function to handle error messages.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Try to retrieve the 'self' instance
                self_instance = args[0] if args else None
                # Format the exception details
                error_message = f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}"
                # Call the provided update_error_log method
                if self_instance and hasattr(self_instance, update_error_log.__name__):
                    getattr(self_instance, update_error_log.__name__)(error_message)
                else:
                    print(error_message)  # Fallback to print if no UI handler is found
        return wrapper
    return decorator


class Event():

    def __init__(self, ui):
        self.ui = ui
        self.mode = "Normal"
        self.filepath = get_resource_path("./config.txt")

        # # 启动日志监控任务
        # self.log_worker = Worker(self.start_log_monitor)
        # self.log_worker.start()

    @catch_exceptions(catch_exceptions)
    def run_dayz(self, program, server = False):
        # 实例化 Worker，并传入回调函数和参数
        self.dayzWorker = Worker(run, self.update_error_log, self.mode, program, server)
        self.dayzWorker.start()  # 启动子线程
        
    def on_mode_select(self, mode):
        self.ui.button_normal.setChecked(False)
        self.ui.button_mission.setChecked(False)
        if (mode == "normal"):
            self.ui.button_normal.setChecked(True)
        if (mode == "mission"):
            self.ui.button_mission.setChecked(True)
        self.mode = mode

    def start_log_monitor(self):
        # 调用 logger.py 中的日志监控函数，并传入回调函数
        log_directory = r"C:\Users\Sky9th\AppData\Local\DayZ"  # 设置日志目录路径
        monitor_script_logs(log_directory, self.ui.update_log)  # 通过回调函数接收日志

    def on_config_update(self, value, key):
        self.ui.config[key] = value
        print(self.ui.config)
        self.save_config()

    def save_config(self):
        """Save the current configuration to a file."""
        self.ui.config['selected'] = ",".join(self.ui.config['selected_mods'])
        
        with open(self.filepath, "w") as file:
            for key, value in self.ui.config.items():
                print(f"{key}={value}\n")
                file.write(f"{key}={value}\n")
    
    def update_log(self, message):
        # 在 UI 中显示日志
        #self.log_label.setText(message)
        print(message)

    def update_error_log(self, message):
        self.ui.update_error_log(message)

    def kill_dayz_server(self):
        """结束 DayZServer_x64.exe 进程"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 检查进程名称
                if proc.info['name'] == 'DayZServer_x64.exe':
                    proc.terminate()  # 终止进程
                    print("DayZServer_x64.exe 已终止")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        print("未找到 DayZServer 进程")
        return False
    
    def kill_dayz(self):
        """结束 DayZ_x64.exe 进程"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 检查进程名称
                if proc.info['name'] == 'DayZ_x64.exe':
                    proc.terminate()  # 终止进程
                    print("DayZ_x64.exe 已终止")
                # 检查进程名称
                if proc.info['name'] == 'DayZDiag_x64.exe':
                    proc.terminate()  # 终止进程
                    print("DayZDiag_x64.exe 已终止")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        print("未找到 DayZ 进程")
        return False

    def kill_dayz_processes(self):
        """结束所有 DayZ 相关的进程"""
        dayz_server_killed = self.kill_dayz_server()
        dayz_killed = self.kill_dayz()
        
        if not dayz_server_killed and not dayz_killed:
            print("没有找到 DayZ 相关的进程需要终止")
        else:
            print("所有相关进程已终止")