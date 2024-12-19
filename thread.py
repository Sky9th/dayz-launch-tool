import threading
import traceback
import queue

class Worker(threading.Thread):
    def __init__(self, callback, error_callback=None, *args, **kwargs):
        """
        Worker 构造函数

        :param callback: 子线程运行的回调函数
        :param error_callback: 捕获异常时调用的回调函数（通常更新错误日志）
        :param args: 回调函数的参数（可选）
        :param kwargs: 回调函数的关键字参数（可选）
        """
        super().__init__()
        self.callback = callback
        self.error_callback = error_callback
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            print("Running callback in worker...")
            # 调用传入的回调函数
            result = self.callback(*self.args, **self.kwargs)
            print(f"Callback result: {result}")
        except Exception as e:
            error_message = f"Exception in thread {self.name}: {str(e)}\n{traceback.format_exc()}"
            print(error_message)  # 打印异常信息
            if self.error_callback:
                # 调用错误回调函数，将错误信息传递回主线程
                self.error_callback(error_message)
