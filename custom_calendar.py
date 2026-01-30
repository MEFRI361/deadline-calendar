import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from typing import List, Callable


class CustomCalendar(ctk.CTkFrame):
    def __init__(self, parent, tasks: List, color_calculator,
                 on_task_click: Callable, on_date_click: Callable, on_add_task: Callable):
        super().__init__(parent)

        self.tasks = tasks
        self.color_calculator = color_calculator
        self.on_task_click = on_task_click
        self.on_date_click = on_date_click
        self.on_add_task = on_add_task

        self.current_date = datetime.now()
        self.selected_date = None  # Это свойство будет доступно извне
        self.selected_frame = None

        # Кэш для задач по дням
        self.tasks_cache = {}
        # Флаг блокировки на время обновления
        self.is_updating = False

        # Русские названия месяцев
        self.russian_months = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        self.setup_ui()
        self.update_calendar()

    def setup_ui(self):
        # Header with navigation
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=5, pady=5)

        self.prev_btn = ctk.CTkButton(header_frame, text="←", width=30,
                                      command=self.prev_month)
        self.prev_btn.pack(side="left", padx=5)

        self.month_label = ctk.CTkLabel(header_frame, text="",
                                        font=ctk.CTkFont(weight="bold", size=16))
        self.month_label.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(header_frame, text="→", width=30,
                                      command=self.next_month)
        self.next_btn.pack(side="right", padx=5)

        # Week days header
        week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        week_frame = ctk.CTkFrame(self)
        week_frame.pack(fill="x", padx=5, pady=2)

        for day in week_days:
            label = ctk.CTkLabel(week_frame, text=day, width=100, height=30,
                                 font=ctk.CTkFont(weight="bold"))
            label.pack(side="left", padx=1, pady=1)

        # Calendar grid
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def get_russian_month_year(self):
        """Получить русское название месяца и год"""
        month_name = self.russian_months.get(self.current_date.month, "")
        year = self.current_date.year
        return f"{month_name} {year}"

    def get_tasks_for_date(self, date):
        """Получить задачи для даты с использованием кэша"""
        date_key = date.isoformat()
        if date_key not in self.tasks_cache:
            self.tasks_cache[date_key] = [
                task for task in self.tasks
                if task.deadline.date() == date and not task.is_completed
            ]
        return self.tasks_cache[date_key]

    def get_previous_and_next_month_days(self, cal):
        """Получить дни предыдущего и следующего месяца для заполнения календаря"""
        first_week = cal[0]
        last_week = cal[-1]

        # Дни предыдущего месяца
        prev_month_days = []
        prev_month = self.current_date.replace(day=1) - timedelta(days=1)
        last_day_prev_month = calendar.monthrange(prev_month.year, prev_month.month)[1]

        prev_day = last_day_prev_month - first_week.count(0) + 1
        for day in first_week:
            if day == 0:
                prev_month_days.append(prev_day)
                prev_day += 1
            else:
                prev_month_days.append(0)

        # Дни следующего месяца
        next_month_days = []
        next_day = 1
        for day in last_week:
            if day == 0:
                next_month_days.append(next_day)
                next_day += 1
            else:
                next_month_days.append(0)

        return prev_month_days, next_month_days, prev_month

    def update_calendar(self):
        if self.is_updating:
            return

        self.is_updating = True

        # Блокируем кнопки на время обновления
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")

        # Очищаем кэш при обновлении календаря
        self.tasks_cache.clear()

        # Clear previous calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Update month label with Russian month name
        month_year = self.get_russian_month_year()
        self.month_label.configure(text=month_year)

        # Reset selection when changing months
        self.selected_date = None
        self.selected_frame = None

        # Create calendar grid
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)

        # Получаем дни предыдущего и следующего месяца
        prev_month_days, next_month_days, prev_month = self.get_previous_and_next_month_days(cal)

        today_found = False

        # Создаем все недели сразу
        week_frames = []
        for week_idx, week in enumerate(cal):
            week_frame = ctk.CTkFrame(self.calendar_frame)
            week_frames.append(week_frame)

        # Отображаем все недели сразу для быстрой отрисовки
        for week_frame in week_frames:
            week_frame.pack(fill="x", padx=1, pady=1)

        # Быстро создаем все ячейки
        for week_idx, week in enumerate(cal):
            week_frame = week_frames[week_idx]

            for day_idx, day in enumerate(week):
                day_frame = ctk.CTkFrame(week_frame, width=100, height=80)
                day_frame.pack(side="left", padx=1, pady=1)
                day_frame.pack_propagate(False)

                if day != 0:
                    # День текущего месяца
                    date = datetime(self.current_date.year, self.current_date.month, day)
                    self.create_day_widget(day_frame, day, date, is_current_month=True)

                    # Подсветка всех дней при загрузке
                    day_frame.configure(fg_color=("gray90", "gray30"))

                    # Особое выделение для сегодняшнего дня
                    if date.date() == datetime.now().date():
                        day_frame.configure(fg_color=("#87CEEB", "#4682B4"))
                        # Запоминаем сегодняшний день для автоматического выбора
                        if not today_found:
                            self.selected_date = date.date()
                            self.selected_frame = day_frame
                            day_frame.configure(fg_color=("#87CEEB", "#4682B4"))
                            today_found = True
                else:
                    # День предыдущего или следующего месяца
                    if week_idx == 0:
                        # Первая неделя - дни предыдущего месяца
                        prev_day = prev_month_days[day_idx]
                        if prev_day != 0:
                            prev_month_date = prev_month.replace(day=prev_day)
                            self.create_day_widget(day_frame, prev_day, prev_month_date, is_current_month=False)
                        else:
                            self.create_empty_day_widget(day_frame)
                    else:
                        # Последние недели - дни следующего месяца
                        next_day = next_month_days[day_idx]
                        if next_day != 0:
                            next_month = (self.current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
                            next_month_date = next_month.replace(day=next_day)
                            self.create_day_widget(day_frame, next_day, next_month_date, is_current_month=False)
                        else:
                            self.create_empty_day_widget(day_frame)

        # Автоматически показываем задачи на сегодняшний день после создания интерфейса
        if today_found and self.selected_date:
            # Используем after чтобы дать время на создание всего интерфейса
            self.after(10, lambda: self.on_date_click(self.selected_date))

        # Разблокируем кнопки после завершения обновления
        self.after(50, self.enable_navigation)

    def enable_navigation(self):
        """Включить навигацию после завершения обновления"""
        self.is_updating = False
        self.prev_btn.configure(state="normal")
        self.next_btn.configure(state="normal")

    def create_day_widget(self, parent, day, date, is_current_month=True):
        # Store the date in the frame for reference
        parent.date = date
        parent.is_current_month = is_current_month

        # Day number - разные стили для текущего и других месяцев
        if date.date() == datetime.now().date():
            # Сегодняшний день
            day_label = ctk.CTkLabel(parent, text=str(day),
                                     font=ctk.CTkFont(weight="bold"),
                                     text_color=("blue", "lightblue"))
        elif is_current_month:
            # День текущего месяца
            day_label = ctk.CTkLabel(parent, text=str(day),
                                     font=ctk.CTkFont(weight="bold"))
        else:
            # День другого месяца
            day_label = ctk.CTkLabel(parent, text=str(day),
                                     font=ctk.CTkFont(weight="normal"),
                                     text_color=("gray60", "gray50"))
        day_label.pack(anchor="nw", padx=2, pady=2)

        # Показываем задачи только для дней текущего месяца
        if is_current_month:
            # Tasks for this day (используем кэшированную версию)
            day_tasks = self.get_tasks_for_date(date.date())

            # Show first 2 tasks
            for task in day_tasks[:2]:
                task_color = self.color_calculator.get_task_color(task)

                task_btn = ctk.CTkButton(
                    parent,
                    text=task.title[:12] + "..." if len(task.title) > 12 else task.title,
                    fg_color=task_color,
                    text_color="black",
                    height=18,
                    font=ctk.CTkFont(size=9),
                    anchor="w"
                )
                task_btn.pack(fill="x", padx=1, pady=1)
                task_btn.configure(command=lambda t=task: self.on_task_click(t))

            # Show "+ more" if there are more tasks
            if len(day_tasks) > 2:
                more_label = ctk.CTkLabel(parent, text=f"+{len(day_tasks) - 2} еще",
                                          font=ctk.CTkFont(size=8))
                more_label.pack(fill="x", padx=1, pady=1)

        # Single click for selection (только для дней текущего месяца)
        if is_current_month:
            parent.bind("<Button-1>", lambda e, d=date.date(), f=parent: self.select_date(d, f))
            day_label.bind("<Button-1>", lambda e, d=date.date(), f=parent: self.select_date(d, f))

            # Double click for adding task
            parent.bind("<Double-Button-1>", lambda e, d=date: self.add_task_for_date(d))
            day_label.bind("<Double-Button-1>", lambda e, d=date: self.add_task_for_date(d))
        else:
            # Для дней других месяцев делаем неактивными
            parent.configure(fg_color=("gray95", "gray20"))
            day_label.configure(cursor="")

    def create_empty_day_widget(self, parent):
        """Создать полностью пустую ячейку"""
        empty_label = ctk.CTkLabel(parent, text="")
        empty_label.pack(expand=True)

    def select_date(self, date, frame):
        if self.is_updating:
            return

        # Reset ALL day frames to base highlight first
        for week_frame in self.calendar_frame.winfo_children():
            for day_frame in week_frame.winfo_children():
                # Check if this is a day frame with date attribute and current month
                if hasattr(day_frame, 'date') and hasattr(day_frame, 'is_current_month'):
                    if day_frame.is_current_month:
                        # Base highlight for all days of current month
                        if day_frame.date.date() == datetime.now().date():
                            day_frame.configure(fg_color=("#87CEEB", "#4682B4"))
                            frame.configure(fg_color=("#9cd0e6", "#3a6a91"))
                        else:
                            day_frame.configure(fg_color=("gray90", "gray30"))

        frame.configure(fg_color=("gray70", "gray50"))
        self.selected_frame = frame
        self.selected_date = date

        self.on_date_click(date)

    def add_task_for_date(self, date):
        """Открыть окно добавления задачи с предзаполненной датой"""
        if self.is_updating:
            return
        self.on_add_task(date)

    def prev_month(self):
        if self.is_updating:
            return

        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.current_date = self.current_date.replace(day=1)
        self.update_calendar()

    def next_month(self):
        if self.is_updating:
            return

        next_month = self.current_date.month + 1
        next_year = self.current_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        self.current_date = self.current_date.replace(year=next_year, month=next_month, day=1)
        self.update_calendar()

    def update_tasks(self, tasks):
        if self.is_updating:
            return

        self.tasks = tasks
        self.tasks_cache.clear()  # Очищаем кэш при обновлении задач
        self.update_calendar()