import typing as t

class Task:
    def __init__(self, priority, task_type, data):
        self.priority = priority
        self.task_type = task_type
        self.data = data
    def __lt__(self, other):
        return self.priority < other.priority


# 事件管理器类，用于管理和分发事件处理器
class TaskManager(object):
    event_callback_map = dict()  # 用于存储事件类型与处理器的映射关系

    # 初始化事件管理器，将事件类型与事件类进行映射
    def __init__(self):
        pass

    # 注册事件处理器的装饰器
    def register(self, event_type: str) -> t.Callable:
        def decorator(f: t.Callable) -> t.Callable:
            self.register_handler_with_task_type(event_type=event_type, handler=f)
            return f

        return decorator

    # 注册事件处理器，将其与对应的事件类型关联
    @staticmethod
    def register_handler_with_task_type(event_type, handler):
        TaskManager.event_callback_map[event_type] = handler

    # 根据请求数据获取对应的事件处理器
    @staticmethod
    def get_handler_with_task(task:Task) -> t.Callable:
        # 获取事件处理器
        return TaskManager.event_callback_map.get(task.task_type)


task_manager = TaskManager()

