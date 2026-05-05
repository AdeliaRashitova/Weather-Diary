import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
# Имя файла для сохранения данных
DATA_FILE = "weather_diary.json"
class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("850x550")
        self.root.resizable(True, True)
        
        # Список записей
        self.entries = []
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных из файла при запуске
        self.load_from_file()
        
    def create_widgets(self):
        # === Фрейм для ввода ===
        input_frame = tk.LabelFrame(self.root, text="Добавление записи", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now
().strftime("%Y-%m-%d"))
        
        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Описание
        tk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Осадки
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=0, column=4, padx=10, pady=5)
        
        # Кнопка добавления
        tk.Button(input_frame, text="Добавить запись", command=self.add_entry, bg="#4CAF50", fg="white").grid(row=1, column=4, padx=10, pady=5)
        
        # === Фрейм для фильтров ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date = tk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(filter_frame, text="Мин. температура (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp_min = tk.Entry(filter_frame, width=10)
        self.filter_temp_min.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters, bg="#2196F3", fg="white").grid(row=0, column=4, padx=10, pady=5)
        tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters, bg="#FF9800", fg="white").grid(row=0, column=5, padx=10, pady=5)
        
        # === Фрейм для таблицы ===
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание таблицы (Treeview)
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=400)
        self.tree.column("precipitation", width=80)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=s
                            crollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === Фрейм для кнопок управления данными ===
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(control_frame, text="Сохранить в JSON", command=self.save_to_file, bg="#8BC34A", fg="white").pack(side="left", padx=5)
        tk.Button(control_frame, text="Загрузить из JSON", command=self.load_from_file, bg="#FF5722", fg="white").pack(side="left", padx=5)
        tk.Button(control_frame, text="Удалить выбранное", command=self.delete_selected, bg="#F44336", fg="white").pack(side="left", padx=5)
        
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_entry(self):
        """Добавление новой записи"""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Валидация
        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        try:
            temperature = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return
        
        # Создание записи
        entry = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        
        self.entries.append(entry)
        self.refresh_table()
        
        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
        messagebox.showinfo("Успех", "Запись добавлена")
    
    def refresh_table(self, filtered_entries=None):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        entries_to_show = filtered_entries if filtered_entries is not None else self.entries
        
        # Сортировка по дате
        entries_to_show = sorted(entries_to_show, key=lambda x: x["date"])
        
        for entry in entries_to_show:
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                entry["precipitation"]
            ))
    
    def apply_filters(self):
        """Применение фильтров"""
        filtered = self.entries.copy()
        
        # Фильтр по дате
        date_filter = self.filter_date.get().strip()
        if date_filter:
            if self.validate_date(date_filter):
                filtered = [e for e in filtered if e["date"] == date_filter]
            else:
                messagebox.showwarning("Предупреждение", "Неверный формат даты фильтра. Фильтр по дате не применён.")
        
        # Фильтр по минимальной температуре
        temp_filter = self.filter_temp_min.get().strip()
        if temp_filter:
            try:
                min_temp = float(temp_filter)
                filtered = [e for e in filtered if e["temperature"] > min_temp]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Температура фильтра должна быть числом. Фильтр не применён.")
        
        self.refresh_table(filtered)
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_date.delete(0, tk.END)
        self.filter_temp_min.delete(0, tk.END)
        self.refresh_table()
    
    def save_to_file(self):
        """Сохранение в JSON-файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_from_file(self):
        """Загрузка из JSON-файла"""
        if not os.path.exists(DATA_FILE):
            messagebox.showinfo("Информация", "Файл с данными не найден. Будет создан новый при сохранении.")
            return
        
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            self.reset_filters()
            messagebox.showinfo("Успех", f"Загружено {len(self.entries)} записей")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл повреждён или имеет неверный формат JSON")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def delete_selected(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            # Получаем значения выбранной строки
            values = self.tree.item(selected[0])["values"]
            # Находим и удаляем запись из списка
            for i, entry in enumerate(self.entries):
                if (entry["date"] == values[0] and 
                    entry["temperature"] == values[1] and 
                    entry["description"] == values[2]):
                    del self.entries[i]
                    break
            self.refresh_table()
if __name__ == "__main__":
    root = tk.Tk
()
    app = WeatherDiaryApp(root)
    root.mainloop()
        
