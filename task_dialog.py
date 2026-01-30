import customtkinter as ctk
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk


class TaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, task=None, callback=None, preset_date=None):
        super().__init__(parent)

        self.task = task
        self.callback = callback
        self.preset_date = preset_date

        self.title("Добавить/Редактировать задачу" if task else "Добавить задачу")
        self.geometry("500x500")
        self.resizable(False, False)

        self.setup_ui()
        if task:
            self.load_task_data()
        elif preset_date:
            self.load_preset_date()

        self.grab_set()
        self.focus_set()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        ctk.CTkLabel(main_frame, text="Название задачи:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.title_entry = ctk.CTkEntry(main_frame, placeholder_text="Введите название задачи")
        self.title_entry.pack(fill="x", pady=(0, 15))

        # Описание
        ctk.CTkLabel(main_frame, text="Описание (необязательно):",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.desc_text = ctk.CTkTextbox(main_frame, height=80)
        self.desc_text.pack(fill="x", pady=(0, 15))

        # Дедлайн
        deadline_frame = ctk.CTkFrame(main_frame)
        deadline_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(deadline_frame, text="Дедлайн:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        datetime_frame = ctk.CTkFrame(deadline_frame)
        datetime_frame.pack(fill="x", pady=5)

        # Дата
        default_date = datetime.now().strftime("%Y-%m-%d")
        self.date_var = ctk.StringVar(value=default_date)
        date_entry = ctk.CTkEntry(datetime_frame, textvariable=self.date_var, width=120)
        date_entry.pack(side="left", padx=(0, 10))

        # Время
        time_frame = ctk.CTkFrame(datetime_frame)
        time_frame.pack(side="left")

        self.hour_var = ctk.StringVar(value="12")
        self.minute_var = ctk.StringVar(value="00")

        hour_spinbox = ctk.CTkEntry(time_frame, textvariable=self.hour_var, width=40)
        hour_spinbox.pack(side="left")
        ctk.CTkLabel(time_frame, text=":").pack(side="left")
        minute_spinbox = ctk.CTkEntry(time_frame, textvariable=self.minute_var, width=40)
        minute_spinbox.pack(side="left")

        # Приоритет
        priority_frame = ctk.CTkFrame(main_frame)
        priority_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(priority_frame, text="Приоритет:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        self.priority_var = ctk.StringVar(value="Средний")
        priorities = ["Высокий", "Средний", "Низкий"]

        for priority in priorities:
            rb = ctk.CTkRadioButton(priority_frame, text=priority,
                                    variable=self.priority_var, value=priority)
            rb.pack(side="left", padx=10)

        # Статус выполнения
        self.completed_var = ctk.BooleanVar(value=False)
        completed_cb = ctk.CTkCheckBox(main_frame, text="Задача выполнена",
                                       variable=self.completed_var)
        completed_cb.pack(anchor="w", pady=(0, 20))

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")

        save_btn = ctk.CTkButton(button_frame, text="Сохранить",
                                 command=self.save_task)
        save_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(button_frame, text="Отмена",
                                   command=self.destroy, fg_color="transparent",
                                   border_width=1, text_color=("gray10", "gray90"))
        cancel_btn.pack(side="right", padx=5)

        # Кнопка удаления (только для редактирования существующей задачи)
        if self.task:
            delete_btn = ctk.CTkButton(button_frame, text="Удалить",
                                       command=self.confirm_delete,
                                       fg_color="#FF4444", hover_color="#CC3333")
            delete_btn.pack(side="left", padx=5)

    def load_task_data(self):
        if self.task:
            self.title_entry.insert(0, self.task.title)
            if self.task.description:
                self.desc_text.insert("1.0", self.task.description)

            self.date_var.set(self.task.deadline.strftime("%Y-%m-%d"))
            self.hour_var.set(self.task.deadline.strftime("%H"))
            self.minute_var.set(self.task.deadline.strftime("%M"))

            # Конвертируем английский приоритет в русский
            priority_mapping = {"High": "Высокий", "Medium": "Средний", "Low": "Низкий"}
            russian_priority = priority_mapping.get(self.task.priority, "Средний")
            self.priority_var.set(russian_priority)

            self.completed_var.set(self.task.is_completed)

    def load_preset_date(self):
        """Загрузить предустановленную дату"""
        if self.preset_date:
            self.date_var.set(self.preset_date.strftime("%Y-%m-%d"))
            self.hour_var.set(self.preset_date.strftime("%H"))
            self.minute_var.set(self.preset_date.strftime("%M"))

    def save_task(self):
        title = self.title_entry.get().strip()
        if not title:
            self.show_error("Введите название задачи")
            return

        try:
            date_str = self.date_var.get()
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            deadline = datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=hour, minute=minute
            )

            if deadline < datetime.now():
                self.show_error("Дедлайн не может быть в прошлом")
                return

        except ValueError:
            self.show_error("Некорректная дата или время")
            return

        # Конвертируем русский приоритет обратно в английский для хранения
        priority_mapping = {"Высокий": "High", "Средний": "Medium", "Низкий": "Low"}
        english_priority = priority_mapping.get(self.priority_var.get(), "Medium")

        task_data = {
            "title": title,
            "description": self.desc_text.get("1.0", "end-1c").strip(),
            "deadline": deadline,
            "priority": english_priority,
            "is_completed": self.completed_var.get()
        }

        if self.callback:
            self.callback(task_data, self.task)

        self.destroy()

    def confirm_delete(self):
        """Подтверждение удаления задачи"""
        confirm_dialog = DeleteConfirmationDialog(self, self.task.title, self.delete_task)

    def delete_task(self):
        """Удалить задачу после подтверждения"""
        if self.task and self.callback:
            # Передаем специальный сигнал для удаления
            self.callback(None, self.task, delete=True)
        self.destroy()

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Ошибка")
        error_window.geometry("300x100")

        ctk.CTkLabel(error_window, text=message).pack(expand=True)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)


class DeleteConfirmationDialog(ctk.CTkToplevel):
    """Диалог подтверждения удаления"""

    def __init__(self, parent, task_title, delete_callback):
        super().__init__(parent)

        self.delete_callback = delete_callback

        self.title("Подтверждение удаления")
        self.geometry("400x200")
        self.resizable(False, False)

        # Центрируем диалог относительно родителя
        self.transient(parent)
        self.grab_set()

        self.setup_ui(task_title)

    def setup_ui(self, task_title):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Иконка предупреждения и текст
        warning_frame = ctk.CTkFrame(main_frame)
        warning_frame.pack(fill="x", pady=(0, 20))

        # Текст предупреждения
        warning_text = f"Вы уверены, что хотите удалить задачу?\n\n\"{task_title}\""
        warning_label = ctk.CTkLabel(warning_frame, text=warning_text,
                                     font=ctk.CTkFont(size=14),
                                     justify="center")
        warning_label.pack(pady=10)

        # Подсказка
        hint_label = ctk.CTkLabel(warning_frame, text="Это действие нельзя отменить",
                                  text_color=("gray50", "gray40"),
                                  font=ctk.CTkFont(size=12))
        hint_label.pack(pady=(0, 10))

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")

        # Кнопка удаления
        delete_btn = ctk.CTkButton(button_frame, text="Удалить",
                                   command=self.confirm_delete,
                                   fg_color="#FF4444", hover_color="#CC3333")
        delete_btn.pack(side="right", padx=5)

        # Кнопка отмены
        cancel_btn = ctk.CTkButton(button_frame, text="Отмена",
                                   command=self.destroy,
                                   fg_color="transparent",
                                   border_width=1,
                                   text_color=("gray10", "gray90"))
        cancel_btn.pack(side="right", padx=5)

    def confirm_delete(self):
        """Подтвердить удаление"""
        if self.delete_callback:
            self.delete_callback()
        self.destroy()