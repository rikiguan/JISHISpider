from queue import PriorityQueue


class Task:
    def __init__(self, priority, task_type, data):
        self.priority = priority
        self.task_type = task_type
        self.data = data
    def __lt__(self, other):
        return self.priority < other.priority

msgpq = PriorityQueue()
pq = PriorityQueue()