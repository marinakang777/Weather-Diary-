import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "weather_data.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("700x500")
        self.records = self.load_data()

        # Поля ввода
        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").pack(pady=2)
        self.date_entry = tk.Entry(root, width=30)
        self.date_entry.pack()

        tk.Label(root, text="Температура (°C):").pack(pady=2)
        self.temp_entry = tk.Entry(root, width=30)
        self.temp_entry.pack()

        tk.Label(root, text="Описание погоды:").pack(pady=2)
        self.desc_entry = tk.Entry(root, width=50)
        self.desc_entry.pack()

        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Осадки", variable=self.precip_var).pack(pady=5)

        # Кнопка добавления
        self.add_btn = tk.Button(root, text="Добавить запись", command=self.add_record)
        self.add_btn.pack(pady=5)

        # Фильтры
        filter_frame = tk.LabelFrame(root, text="Фильтрация")
        filter_frame.pack(pady=10, fill="x", padx=10)

        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=2)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Температура выше:").grid(row=1, column=0, padx=5, pady=2)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, sticky="w")

        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=2, column=0, columnspan=2, pady=5)

        self.reset_filter_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=3, column=0, columnspan=2, pady=5)

        # Таблица для отображения записей
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Загрузка и отображение данных
        self.update_display()

        # Сохранение при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)

    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        # Валидация
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        try:
            temp_val = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        record = {
            "date": date,
            "temperature": temp_val,
            "description": desc,
            "precipitation": "Да" if precip else "Нет"
        }
        self.records.append(record)
        self.save_data()
        self.update_display()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def update_display(self, filtered_records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        records_to_show = filtered_records if filtered_records is not None else self.records
        for rec in records_to_show:
            self.tree.insert("", tk.END, values=(
                rec["date"], rec["temperature"], rec["description"], rec["precipitation"]
            ))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()

        filtered = self.records[:]

        if filter_date:
            try:
                datetime.strptime(filter_date, "%Y-%m-%d")
                filtered = [r for r in filtered if r["date"] == filter_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре")
                return

        if filter_temp:
            try:
                temp_thresh = float(filter_temp)
                filtered = [r for r in filtered if r["temperature"] > temp_thresh]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return

        self.update_display(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_display()

    def on_closing(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
