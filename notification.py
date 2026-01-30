from datetime import datetime, timedelta
from typing import List
from plyer import notification
import time


class NotificationManager:
    def __init__(self):
        self.shown_notifications = set()

    def get_due_tasks(self, tasks: List) -> List:
        now = datetime.now()
        due_tasks = []

        for task in tasks:
            if task.is_completed:
                continue

            time_diff = task.deadline - now
            days_diff = time_diff.total_seconds() / (60 * 60 * 24)

            # Уведомления за 1-3 дня
            if 0 <= days_diff <= 3:
                notification_id = f"{task.id}_{task.deadline.date()}"
                if notification_id not in self.shown_notifications:
                    due_tasks.append(task)
                    self.shown_notifications.add(notification_id)

        return due_tasks

    def show_notification(self, task):
        try:
            days_left = (task.deadline - datetime.now()).days
            message = f"Дедлайн: {task.deadline.strftime('%d.%m.%Y %H:%M')}"
            if days_left > 0:
                message = f"Осталось {days_left} дней. {message}"

            notification.notify(
                title=f"Напоминание: {task.title}",
                message=message,
                timeout=10,
                app_name="Календарь дедлайнов"
            )
        except Exception as e:
            print(f"Ошибка уведомления: {e}")