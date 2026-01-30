import customtkinter as ctk
from custom_calendar import CustomCalendar
from task_dialog import TaskDialog
from storage import StorageManager
from notification import NotificationManager
from color_scheme import ColorSchemeCalculator
import threading
import time
from datetime import datetime


class DeadlineCalendarApp:
    def __init__(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Календарь дедлайнов с цветовой маркировкой")
        self.root.geometry("1000x685")
        self.root.resizable(False, False)

        # Минимальный размер окна
        self.root.minsize(1050, 685)

        self.storage = StorageManager()
        self.notification_manager = NotificationManager()
        self.color_calculator = ColorSchemeCalculator()

        self.tasks = self.storage.load_tasks()

        self.setup_ui()
        self.start_background_services()

    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(main_frame, text="Календарь дедлайнов",
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)

        # Content frame
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Calendar frame
        calendar_frame = ctk.CTkFrame(content_frame)
        calendar_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Calendar
        self.calendar = CustomCalendar(calendar_frame, self.tasks, self.color_calculator,
                                       self.on_task_click, self.on_date_click, self.add_task_for_date)
        self.calendar.pack(fill="both", expand=True, padx=5, pady=5)

        # Controls frame
        controls_frame = ctk.CTkFrame(content_frame, width=280)
        controls_frame.pack(side="right", fill="y", padx=(0, 5), pady=5)
        controls_frame.pack_propagate(False)

        # Buttons
        add_btn = ctk.CTkButton(controls_frame, text="Добавить задачу",
                                command=self.add_task)
        add_btn.pack(pady=10, padx=10, fill="x")

        export_btn = ctk.CTkButton(controls_frame, text="Экспорт в JSON",
                                   command=self.export_tasks)
        export_btn.pack(pady=5, padx=10, fill="x")

        import_btn = ctk.CTkButton(controls_frame, text="Импорт из JSON",
                                   command=self.import_tasks)
        import_btn.pack(pady=5, padx=10, fill="x")

        # Tasks list for selected date
        self.tasks_list_frame = ctk.CTkFrame(controls_frame)
        self.tasks_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tasks_label = ctk.CTkLabel(self.tasks_list_frame, text="Задачи на выбранную дату:",
                                        font=ctk.CTkFont(weight="bold"))
        self.tasks_label.pack(pady=5)

        self.tasks_scrollable = ctk.CTkScrollableFrame(self.tasks_list_frame)
        self.tasks_scrollable.pack(fill="both", expand=True)

    def on_task_click(self, task):
        """Обработчик клика по задаче"""
        dialog = TaskDialog(self.root, task, self.save_task)

    def on_date_click(self, date):
        """Обработчик клика по дате"""
        # Используем after для отложенного обновления
        self.after(10, lambda: self.show_tasks_for_date(date))

    def add_task_for_date(self, date):
        """Добавить задачу на конкретную дату (по двойному клику)"""
        # Создаем datetime с временем по умолчанию (12:00)
        deadline = datetime.combine(date.date(), datetime.strptime("12:00", "%H:%M").time())
        dialog = TaskDialog(self.root, None, self.save_task, preset_date=deadline)

    def add_task(self):
        """Добавить новую задачу"""
        # Получаем выбранную дату из календаря
        selected_date = self.calendar.selected_date
        preset_date = None

        if selected_date:
            # Используем выбранную дату с временем по умолчанию (12:00)
            preset_date = datetime.combine(selected_date, datetime.strptime("12:00", "%H:%M").time())
        else:
            # Если дата не выбрана, используем сегодняшнюю дату
            preset_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)

        dialog = TaskDialog(self.root, None, self.save_task, preset_date=preset_date)

    def show_tasks_for_date(self, date):
        """Показать задачи для выбранной даты"""
        # Очищаем предыдущий список
        for widget in self.tasks_scrollable.winfo_children():
            widget.destroy()

        date_tasks = [task for task in self.tasks if task.deadline.date() == date]

        # Обновляем заголовок
        self.tasks_label.configure(text=f"Задачи на {date.strftime('%d.%m.%Y')}:")

        if not date_tasks:
            no_tasks_label = ctk.CTkLabel(self.tasks_scrollable, text="Нет задач на эту дату")
            no_tasks_label.pack(pady=10)
            return

        for task in date_tasks:
            task_frame = ctk.CTkFrame(self.tasks_scrollable)
            task_frame.pack(fill="x", pady=2, padx=5)

            color = self.color_calculator.get_task_color(task)

            # Main task info
            info_frame = ctk.CTkFrame(task_frame, fg_color=color)
            info_frame.pack(fill="x", padx=1, pady=1)

            # Конвертируем приоритет для отображения
            priority_mapping = {"High": "Высокий", "Medium": "Средний", "Low": "Низкий"}
            russian_priority = priority_mapping.get(task.priority, "Средний")

            title_label = ctk.CTkLabel(info_frame, text=f"{task.title} ({russian_priority})",
                                       font=ctk.CTkFont(weight="bold"),
                                       text_color="black")
            title_label.pack(side="left", padx=5, pady=2)

            time_label = ctk.CTkLabel(info_frame,
                                      text=task.deadline.strftime("%H:%M"),
                                      text_color="black")
            time_label.pack(side="right", padx=5, pady=2)

            # Клик по задаче
            task_frame.bind("<Button-1>", lambda e, t=task: self.on_task_click(t))
            info_frame.bind("<Button-1>", lambda e, t=task: self.on_task_click(t))
            title_label.bind("<Button-1>", lambda e, t=task: self.on_task_click(t))
            time_label.bind("<Button-1>", lambda e, t=task: self.on_task_click(t))

    def save_task(self, task_data, original_task=None, delete=False):
        """Сохранить или удалить задачу"""
        if delete and original_task:
            # Удаляем задачу
            self.tasks.remove(original_task)
            print(f"🗑️ Задача удалена: {original_task.title}")
        elif original_task:
            # Обновляем существующую задачу
            original_task.title = task_data["title"]
            original_task.description = task_data["description"]
            original_task.deadline = task_data["deadline"]
            original_task.priority = task_data["priority"]
            original_task.is_completed = task_data["is_completed"]
            print(f"✏️ Задача обновлена: {original_task.title}")
        else:
            # Добавляем новую задачу
            from storage import Task
            new_task = Task(
                title=task_data["title"],
                description=task_data["description"],
                deadline=task_data["deadline"],
                priority=task_data["priority"],
                is_completed=task_data["is_completed"]
            )
            self.tasks.append(new_task)
            print(f"✅ Задача добавлена: {new_task.title}")

        self.storage.save_tasks(self.tasks)
        # Отложенное обновление календаря
        self.after(50, lambda: self.calendar.update_tasks(self.tasks))

        # Обновляем список задач если дата выбрана
        if self.calendar.selected_date:
            self.after(100, lambda: self.show_tasks_for_date(self.calendar.selected_date))

    def export_tasks(self):
        """Экспорт задач в JSON"""
        filename = ctk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            self.storage.export_tasks(self.tasks, filename)
            print(f"📤 Задачи экспортированы в: {filename}")

    def import_tasks(self):
        """Импорт задач из JSON"""
        filename = ctk.filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            imported_tasks = self.storage.import_tasks(filename)
            if imported_tasks is not None:
                self.tasks = imported_tasks
                self.storage.save_tasks(self.tasks)
                # Отложенное обновление календаря
                self.after(50, lambda: self.calendar.update_tasks(self.tasks))
                print(f"📥 Задачи импортированы из: {filename}")

    def start_background_services(self):
        """Запуск фоновых сервисов"""

        def check_notifications():
            while True:
                due_tasks = self.notification_manager.get_due_tasks(self.tasks)
                for task in due_tasks:
                    self.notification_manager.show_notification(task)
                time.sleep(60)  # Проверка каждую минуту

        notification_thread = threading.Thread(target=check_notifications, daemon=True)
        notification_thread.start()

        # Автосохранение каждые 5 минут
        def auto_save():
            while True:
                time.sleep(300)
                self.storage.save_tasks(self.tasks)

        save_thread = threading.Thread(target=auto_save, daemon=True)
        save_thread.start()

    def after(self, ms, func):
        """Обертка для root.after"""
        return self.root.after(ms, func)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DeadlineCalendarApp()
    app.run()