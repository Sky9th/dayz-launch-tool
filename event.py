import os
import sys

import psutil
from run import run
from thread import Worker
from logger import LogMonitor  # 导入 logger 的监控日志函数
import traceback
import threading

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
        print("Event init")
        self.ui = ui
        self.mode = "normal"
        self.filepath = get_resource_path("./config.txt")
        self.monitor_client_worker = None
        self.monitor_server_worker = None

    @catch_exceptions(catch_exceptions)
    def run_dayz(self, program, server = False):
        if(self.ui.config["kill_before_start"] == "True"):
            self.kill_dayz()

        # 实例化 Worker，并传入回调函数和参数
        self.dayzWorker = Worker(run, self.mode, program, server)
        self.dayzWorker.start()  # 启动子线程

        self.create_log_worker(server)
        
    def create_log_worker(self, server):
        # 检查并结束现有线程
        if server:
            if hasattr(self, "server_worker") and self.server_worker and self.server_worker.isRunning():
                print("Stopping existing server thread...")
                self.stop_server_event.set()  # 设置停止标志
                self.server_worker.wait(5000)  # 等待线程结束，最多5秒
                print("Existing server thread stopped.")
        else:
            if hasattr(self, "client_worker") and self.client_worker and self.client_worker.isRunning():
                print("Stopping existing client thread...")
                self.stop_client_event.set()  # 设置停止标志
                self.client_worker.wait(5000)  # 等待线程结束，最多5秒
                print("Existing client thread stopped.")

        # 创建新的 `stop_event` 和 `LogMonitor` 实例
        log_directory = self.ui.config["dayZInstallPath"]
        if server:
            self.stop_server_event = threading.Event()  # 创建停止标志
            log_directory += "\ServerProfile"
            monitor = LogMonitor(log_directory, self.ui.log_update_server_signal, stop_event=self.stop_server_event)
            self.server_worker = Worker(monitor.monitor)  # 创建服务器监控线程
            self.server_worker.start()  # 启动服务器线程
        else:
            self.stop_client_event = threading.Event()  # 创建停止标志
            log_directory += "\ClientProfile"
            monitor = LogMonitor(log_directory, self.ui.log_update_client_signal, stop_event=self.stop_client_event)
            self.client_worker = Worker(monitor.monitor)  # 创建客户端监控线程
            self.client_worker.start()  # 启动客户端线程
        
    def on_mode_select(self, mode):
        self.ui.button_normal.setChecked(False)
        self.ui.button_mission.setChecked(False)
        if (mode == "normal"):
            self.ui.button_normal.setChecked(True)
        if (mode == "mission"):
            self.ui.button_mission.setChecked(True)
        self.mode = mode

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