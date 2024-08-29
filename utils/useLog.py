import atexit
from functools import wraps
import threading
import json
# 全局字典，用于记录API请求量
request_count = {}
thread_count = {}
task_type_count={}

request_lock = threading.Lock()
thread_lock = threading.Lock()

def save_data_to_file(filename):
    data = {
        'request_count': request_count,
        'thread_count': thread_count,
        'task_type_count': task_type_count
    }
    with open(filename, 'w') as file:
        json.dump(data, file)

def load_data_from_file(filename):
    global request_count, thread_count, task_type_count
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            request_count = data.get('request_count', {})
            thread_count = data.get('thread_count', {})
            task_type_count = data.get('task_type_count', {})
    except FileNotFoundError:
        # 如果文件不存在，初始化为空字典
        request_count = {}
        thread_count = {}
        task_type_count = {}
load_data_from_file('data/data.json')
@atexit.register
def cleanup():
    save_data_to_file('data/data.json')


def log_request(api_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with request_lock:
                if api_name in request_count:
                    request_count[api_name] += 1
                else:
                    request_count[api_name] = 1
                cleanup()
                # 执行实际的API处理函数
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_thread():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with thread_lock:
                # 更新全局字典中的请求量
                if args[0] in thread_count:
                    thread_count[args[0]] += 1
                else:
                    thread_count[args[0]] = 1
                if args[2].task_type  in task_type_count:
                    task_type_count[args[2].task_type] += 1
                else:
                    task_type_count[args[2].task_type] = 1
                cleanup()
                # 执行实际的API处理函数
            return func(*args, **kwargs)
        return wrapper
    return decorator