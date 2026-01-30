from datetime import datetime
from enum import Enum

class Priority(Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"

class TaskItem:
    def __init__(self, title: str, deadline: datetime, priority: Priority = Priority.MEDIUM,
                 description: str = "", category: str = "Общая", is_completed: bool = False, uid: str = None):
        import uuid
        self.uid = uid or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.category = category
        self.is_completed = is_completed