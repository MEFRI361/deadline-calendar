class ColorSchemeCalculator:
    def __init__(self):
        # Обновляем для работы с английскими приоритетами (они хранятся внутри)
        self.priority_colors = {
            "High": "#FF4444",  # Красный
            "Medium": "#FFA500",  # Оранжевый
            "Low": "#44FF44"  # Зеленый
        }
        self.completed_color = "#888888"  # Серый

    def get_task_color(self, task):
        if task.is_completed:
            return self.completed_color
        return self.priority_colors.get(task.priority, "#44FF44")

    def get_priority_color(self, priority):
        return self.priority_colors.get(priority, "#44FF44")