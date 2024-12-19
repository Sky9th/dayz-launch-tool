import threading
from PySide6.QtCore import QThread

class Worker(QThread):
    def __init__(self, callback, *args, **kwargs):
        """
        Worker 构造函数
        :param callback: 要在线程中执行的函数
        :param args: 回调函数的参数
        :param kwargs: 回调函数的关键字参数
        """
        super().__init__()
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        线程运行入口
        """
        try:
            print("Worker thread started.")
            # 将 `stop_event` 注入到回调参数中
            self.callback(*self.args, **self.kwargs)
        except Exception as e:
            print(f"Exception in worker: {str(e)}")
        finally:
            print("Worker thread has stopped.")
