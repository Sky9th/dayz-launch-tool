import os
import sys
from functools import partial

import psutil
from thread import Worker
from logger import LogMonitor  # 导入 logger 的监控日志函数
import threading

from util import get_resource_path
from pack import PackThread
from run import DayZRunThread


class Event():

    def __init__(self, ui):
        print("Event init")
        self.ui = ui
        self.mode = "normal"
        self.filepath = get_resource_path("./config.txt")
        self.monitor_client_worker = None
        self.monitor_server_worker = None

    def pack_pbo(self, program, server = False):
        self.ui.update_error_log("packing pbo.....")
        self.packWorker = PackThread(self.ui.config, self.kill_dayz_processes)
        self.packWorker.progress_signal.connect(self.ui.update_pack_status)
        self.packWorker.pack_signal.connect(partial(self.run_dayz, program, server))
        self.packWorker.start()  # 启动子线程

    def run_dayz(self, program, server, folder_sizes):
        self.ui.update_error_log("run dayz game.....")
        self.on_config_update(folder_sizes, "folderSize")
        self.gameWorker = DayZRunThread(self.mode, program, server, self.ui.config)
        self.gameWorker.start()

        self.gameWorker.run_signal.connect(partial(self.create_log_worker, server))
        
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
        if server:
            log_directory = self.ui.config["dayZServerInstallPath"]
            self.stop_server_event = threading.Event()  # 创建停止标志
            log_directory += "\ServerDebugProfile"
            monitor = LogMonitor(log_directory, self.ui.log_update_server_signal, stop_event=self.stop_server_event)
            self.server_worker = Worker(monitor.monitor)  # 创建服务器监控线程
            self.server_worker.start()  # 启动服务器线程
        else:
            log_directory = self.ui.config["dayZInstallPath"]
            self.stop_client_event = threading.Event()  # 创建停止标志
            log_directory += "\ClientDebugProfile"
            monitor = LogMonitor(log_directory, self.ui.log_update_client_signal, stop_event=self.stop_client_event)
            self.client_worker = Worker(monitor.monitor)  # 创建客户端监控线程
            self.client_worker.start()  # 启动客户端线程
        
    def on_mode_select(self, mode):
        self.ui.button_normal.setChecked(False)
        self.ui.button_mission.setChecked(False)
        if (mode == "MainMenu"):
            self.ui.button_normal.setChecked(True)
        if (mode == "AutoConnect"):
            self.ui.button_mission.setChecked(True)
        self.mode = mode

    def on_config_update(self, value, key):
        self.ui.config[key] = value
        self.save_config()

    def save_config(self):
        """Save the current configuration to a file."""
        self.ui.config['selected'] = ",".join(self.ui.config['selected_mods'])
        
        with open(self.filepath, "w") as file:
            for key, value in self.ui.config.items():
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