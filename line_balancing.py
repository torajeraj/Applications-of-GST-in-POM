import tkinter as tk
from tkinter import ttk, messagebox

class LineBalancingForm(tk.Frame):
    def __init__(self, parent, result_widget):
        super().__init__(parent)
        self.result_widget = result_widget
        self.tasks = []
        self.create_widgets()

    def create_widgets(self):
        # جدول ورودی فعالیت‌ها
        cols = ("Task name", "Time lower", "Time upper", "Predecessors")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=8)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # دکمه افزودن فعالیت
        add_btn = tk.Button(self, text="Add Task", command=self.add_task_row)
        add_btn.pack(side=tk.TOP, padx=5, pady=5)

        # ورودی پارامترهای کلی
        param_frame = tk.Frame(self)
        param_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(param_frame, text="Total Accessible Time [lower, upper]:").grid(row=0, column=0, sticky='w')
        self.total_accessible_lower = tk.Entry(param_frame, width=10)
        self.total_accessible_upper = tk.Entry(param_frame, width=10)
        self.total_accessible_lower.grid(row=0, column=1, padx=2)
        self.total_accessible_upper.grid(row=0, column=2, padx=2)

        tk.Label(param_frame, text="Total Demand [lower, upper]:").grid(row=1, column=0, sticky='w')
        self.total_demand_lower = tk.Entry(param_frame, width=10)
        self.total_demand_upper = tk.Entry(param_frame, width=10)
        self.total_demand_lower.grid(row=1, column=1, padx=2)
        self.total_demand_upper.grid(row=1, column=2, padx=2)

        tk.Label(param_frame, text="Cycle Time [lower, upper]:").grid(row=2, column=0, sticky='w')
        self.cycle_time_lower = tk.Entry(param_frame, width=10)
        self.cycle_time_upper = tk.Entry(param_frame, width=10)
        self.cycle_time_lower.grid(row=2, column=1, padx=2)
        self.cycle_time_upper.grid(row=2, column=2, padx=2)

        # دکمه اجرای الگوریتم
        run_btn = tk.Button(self, text="Run Line Balancing", command=self.run_algorithm)
        run_btn.pack(side=tk.TOP, pady=10)

    def add_task_row(self):
        # اضافه کردن یك ردیف جدید با مقداردهی اولیه خالی به جدول
        new_task_name = f"Task{len(self.tasks)+1}"
        self.tasks.append(new_task_name)
        self.tree.insert("", "end", values=(new_task_name, "", "", ""))
        # بعداً می‌توان تنظیمات بیشتری اضافه کرد مانند Combobox در Predecessors با اسامی tasks

    def run_algorithm(self):
        # دریافت داده ها از جدول و بررسی ورودی ها - آماده انجام الگوریتم
        items = self.tree.get_children()
        task_data = []
        for item in items:
            vals = self.tree.item(item)["values"]
            task_name = vals[0]
            try:
                time_lower = float(vals[1])
                time_upper = float(vals[2])
                if time_lower > time_upper:
                    messagebox.showerror("Input error", f"Lower time > upper time in {task_name}")
                    return
            except:
                messagebox.showerror("Input error", f"Invalid time input in {task_name}")
                return
            preds = vals[3].split(",") if vals[3] else []
            task_data.append({"name": task_name, "time": (time_lower, time_upper), "predecessors": preds})
        
        # خواندن پارامترهای کلی
        try:
            total_accessible = (float(self.total_accessible_lower.get()), float(self.total_accessible_upper.get()))
            total_demand = (float(self.total_demand_lower.get()), float(self.total_demand_upper.get()))
            cycle_time = (self.cycle_time_lower.get(), self.cycle_time_upper.get())
            # اگر cycle_time خالی نباشد مقدار را باید چک کرد و یا محاسبه نمود
        except:
            messagebox.showerror("Input error", "Invalid parameter inputs")
            return

        # فعلاً فقط نمایش داده‌ها برای تست
        res_text = "Tasks:\n"
        for t in task_data:
            res_text += f"{t['name']}: Time={t['time']}, Predecessors={t['predecessors']}\n"
        res_text += f"\nParameters:\nTotal Accessible Time: {total_accessible}\nTotal Demand: {total_demand}\nCycle Time: {cycle_time}\n"

        self.result_widget.delete("1.0", "end")
        self.result_widget.insert("end", res_text)

