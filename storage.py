import json
import os
from datetime import datetime
from typing import List, Optional
import uuid


class Task:
    def __init__(self, title: str, deadline: datetime, priority: str = "Medium",
                 description: str = "", is_completed: bool = False, task_id: Optional[str] = None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.is_completed = is_completed

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
            "priority": self.priority,
            "is_completed": self.is_completed
        }

    @classmethod
    def from_dict(cls, data):
        # Конвертируем старые русские приоритеты в английские при загрузке
        priority_mapping_ru_to_en = {
            "Высокий": "High",
            "Средний": "Medium",
            "Низкий": "Low",
            "High": "High",
            "Medium": "Medium",
            "Low": "Low"
        }

        priority = data["priority"]
        english_priority = priority_mapping_ru_to_en.get(priority, "Medium")

        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data["description"],
            deadline=datetime.fromisoformat(data["deadline"]),
            priority=english_priority,
            is_completed=data["is_completed"]
        )


class StorageManager:
    def __init__(self, filename: str = "data.json"):
        self.filename = filename

    def load_tasks(self) -> List[Task]:
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tasks = []
            for task_data in data:
                try:
                    task = Task.from_dict(task_data)
                    tasks.append(task)
                except (KeyError, ValueError) as e:
                    print(f"Ошибка загрузки задачи: {e}")
                    continue

            return tasks

        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки файла: {e}")
            return []

    def save_tasks(self, tasks: List[Task]):
        try:
            data = [task.to_dict() for task in tasks]

            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except IOError as e:
            print(f"Ошибка сохранения: {e}")

    def export_tasks(self, tasks: List[Task], filename: str):
        try:
            data = [task.to_dict() for task in tasks]

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except IOError as e:
            print(f"Ошибка экспорта: {e}")

    def import_tasks(self, filename: str) -> Optional[List[Task]]:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tasks = []
            for task_data in data:
                try:
                    task = Task.from_dict(task_data)
                    tasks.append(task)
                except (KeyError, ValueError) as e:
                    print(f"Ошибка импорта задачи: {e}")
                    continue

            return tasks

        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка импорта файла: {e}")
            return None