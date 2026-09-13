import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import json
import math
import random

# از ماژول‌های پروژه برای محاسبات خاکستری و مقایسه‌ها استفاده می‌کنیم
from grey_comparison import GreyNumberBatchComparator, MinimaxRegretApproach
from grey_number_operation import grey_subtract, grey_add, grey_divide, grey_multiply


class COMSOLInput(tk.Frame):
    """
    فرم ورود داده + اجرای کامل الگوریتم COMSOL (Randomized among Z>=0)
    - گام 1: نمایش precedence (متنی)
    - گام 2: محاسبه/انتخاب Cycle Time با روش Regret (مثل روش‌های قبلی)
    - محاسبه LB_set از مجموع زمان‌ها / C*
    - اجرای K iteration؛ هر بار بهترین جواب تا آن مرحله را نگه می‌داریم؛
      اگر به LB_min برسیم زودتر توقف می‌کنیم.
    - لاگ گام‌به‌گام همه مراحل در پنجره نتایج نوشته می‌شود (قابل کپی).
    """
    def __init__(self, parent, result_widget):
        super().__init__(parent, bg="#2a2a2a")
        self.result_widget = result_widget
        self.tasks = []
        self.selected_item = None
        self.final_cycle_time = None  # C* نهایی

        # جدول وظایف
        self.tree = ttk.Treeview(
            self,
            columns=("task", "time", "pred"),
            show="headings",
            height=6
        )
        self.tree.heading("task", text="Task")
        self.tree.heading("time", text="Time [a,b]")
        self.tree.heading("pred", text="Predecessors")

        self.tree.column("task", width=80)
        self.tree.column("time", width=120)
        self.tree.column("pred", width=200)
        self.tree.pack(fill="x", pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # فرم ورود داده
        form = tk.Frame(self, bg="#2a2a2a")
        form.pack(fill="x", pady=5)

        tk.Label(form, text="Task:", bg="#2a2a2a", fg="white").grid(row=0, column=0)
        self.task_entry = tk.Entry(form, width=10)
        self.task_entry.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Lower:", bg="#2a2a2a", fg="white").grid(row=0, column=2)
        self.lower_entry = tk.Entry(form, width=7)
        self.lower_entry.grid(row=0, column=3, padx=2)

        tk.Label(form, text="Upper:", bg="#2a2a2a", fg="white").grid(row=0, column=4)
        self.upper_entry = tk.Entry(form, width=7)
        self.upper_entry.grid(row=0, column=5, padx=2)

        tk.Label(form, text="Predecessors (comma-separated):", bg="#2a2a2a", fg="white").grid(row=0, column=6)
        self.pred_entry = tk.Entry(form, width=25)
        self.pred_entry.grid(row=0, column=7, padx=5)

        # دکمه‌های مدیریت تسک
        btns = tk.Frame(self, bg="#2a2a2a")
        btns.pack(fill="x", pady=5)

        self.add_btn = tk.Button(btns, text="Add Task", command=self.add_task)
        self.add_btn.pack(side="left", padx=5)

        self.update_btn = tk.Button(btns, text="Update Task", command=self.update_task, state="disabled")
        self.update_btn.pack(side="left", padx=5)

        # پارامترها (Accessible, Demand/Cycle, Iterations)
        params = tk.Frame(self, bg="#2a2a2a")
        params.pack(fill="x", pady=10)

        tk.Label(params, text="Total Accessible Time [a,b]:", bg="#2a2a2a", fg="white").grid(row=0, column=0, sticky="w")
        self.access_low = tk.Entry(params, width=7); self.access_low.grid(row=0, column=1, padx=2)
        self.access_up  = tk.Entry(params, width=7); self.access_up.grid(row=0, column=2, padx=2)

        tk.Label(params, text="Total Demand [a,b]:", bg="#2a2a2a", fg="white").grid(row=1, column=0, sticky="w")
        self.demand_low = tk.Entry(params, width=7); self.demand_low.grid(row=1, column=1, padx=2)
        self.demand_up  = tk.Entry(params, width=7); self.demand_up.grid(row=1, column=2, padx=2)

        tk.Label(params, text="Cycle Time [a,b]:", bg="#2a2a2a", fg="white").grid(row=2, column=0, sticky="w")
        self.cycle_low  = tk.Entry(params, width=7); self.cycle_low.grid(row=2, column=1, padx=2)
        self.cycle_up   = tk.Entry(params, width=7); self.cycle_up.grid(row=2, column=2, padx=2)

        # کنترل وابستگی demand و cycle
        self.demand_low.bind("<KeyRelease>", self.toggle_cycle_inputs)
        self.demand_up.bind("<KeyRelease>", self.toggle_cycle_inputs)
        self.cycle_low.bind("<KeyRelease>", self.toggle_demand_inputs)
        self.cycle_up.bind("<KeyRelease>", self.toggle_demand_inputs)

        # تعداد تکرارهای COMSOL
        tk.Label(params, text="Iterations (K):", bg="#2a2a2a", fg="white").grid(row=3, column=0, sticky="w")
        self.iter_entry = tk.Entry(params, width=7)
        self.iter_entry.insert(0, "10")
        self.iter_entry.grid(row=3, column=1, padx=2)

        # دکمه‌های اصلی
        btn_frame = tk.Frame(self, bg="#2a2a2a")
        btn_frame.pack(fill="x", pady=5)

        tk.Button(btn_frame, text="Run COMSOL", command=self.run_comsol).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Show Network", command=self.show_network).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save Project", command=self.save_project).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Load Project", command=self.load_project).pack(side="left", padx=5)

    # ---------- مدیریت جدول ----------
    def add_task(self):
        task = self.task_entry.get().strip()
        lower = self.lower_entry.get().strip()
        upper = self.upper_entry.get().strip()
        preds = self.pred_entry.get().strip()

        if not task or not lower or not upper:
            messagebox.showerror("Error", "Task and both bounds are required")
            return
        try:
            low_val = float(lower); up_val = float(upper)
            if low_val > up_val:
                messagebox.showerror("Error", "Upper bound must be ≥ Lower bound")
                return
        except ValueError:
            messagebox.showerror("Error", "Bounds must be numeric")
            return

        self.tree.insert("", "end", values=(task, f"[{low_val},{up_val}]", preds))
        if task not in self.tasks:
            self.tasks.append(task)
        self.clear_form()

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_item = selected[0]
        values = self.tree.item(self.selected_item, "values")

        self.task_entry.delete(0, tk.END); self.task_entry.insert(0, values[0])
        tlo, tup = values[1].strip("[]").split(",")
        self.lower_entry.delete(0, tk.END); self.lower_entry.insert(0, tlo)
        self.upper_entry.delete(0, tk.END); self.upper_entry.insert(0, tup)
        self.pred_entry.delete(0, tk.END); self.pred_entry.insert(0, values[2])

        self.update_btn.config(state="normal"); self.add_btn.config(state="disabled")

    def update_task(self):
        if not self.selected_item:
            return
        task = self.task_entry.get().strip()
        lower = self.lower_entry.get().strip()
        upper = self.upper_entry.get().strip()
        preds = self.pred_entry.get().strip()

        if not task or not lower or not upper:
            messagebox.showerror("Error", "Task and both bounds are required")
            return
        try:
            low_val = float(lower); up_val = float(upper)
            if low_val > up_val:
                messagebox.showerror("Error", "Upper bound must be ≥ Lower bound")
                return
        except ValueError:
            messagebox.showerror("Error", "Bounds must be numeric")
            return

        self.tree.item(self.selected_item, values=(task, f"[{low_val},{up_val}]", preds))
        if task not in self.tasks:
            self.tasks.append(task)
        self.clear_form()
        self.update_btn.config(state="disabled"); self.add_btn.config(state="normal")
        self.selected_item = None

    def clear_form(self):
        self.task_entry.delete(0, tk.END)
        self.lower_entry.delete(0, tk.END)
        self.upper_entry.delete(0, tk.END)
        self.pred_entry.delete(0, tk.END)

    # ---------- کنترل ورودی‌ها ----------
    def toggle_cycle_inputs(self, event=None):
        if self.demand_low.get() or self.demand_up.get():
            self.cycle_low.config(state="disabled")
            self.cycle_up.config(state="disabled")
        else:
            self.cycle_low.config(state="normal")
            self.cycle_up.config(state="normal")

    def toggle_demand_inputs(self, event=None):
        if self.cycle_low.get() or self.cycle_up.get():
            self.demand_low.config(state="disabled")
            self.demand_up.config(state="disabled")
        else:
            self.demand_low.config(state="normal")
            self.demand_up.config(state="normal")

    # ---------- اجرای کامل COMSOL ----------
    def run_comsol(self):
        # خواندن داده‌ها
        tasks = []
        preds_dict = {}
        for child in self.tree.get_children():
            values = self.tree.item(child, "values")
            name = values[0]
            a, b = values[1].strip("[]").split(",")
            iv = (float(a), float(b))
            preds = [p.strip() for p in values[2].split(",") if p.strip()]
            tasks.append((name, iv, preds))
            preds_dict[name] = preds

        if not tasks:
            messagebox.showwarning("Warning", "No tasks entered.")
            return

        access_low = self.access_low.get().strip()
        access_up = self.access_up.get().strip()
        demand_low = self.demand_low.get().strip()
        demand_up = self.demand_up.get().strip()
        cycle_low = self.cycle_low.get().strip()
        cycle_up = self.cycle_up.get().strip()
        try:
            K = int(self.iter_entry.get().strip() or "10")
            if K <= 0: K = 10
        except:
            K = 10

        # چاپ نتایج
        out = []
        out.append("📊 COMSOL (Randomized among Z≥0)")

        # گام 1: precedence (متنی)
        out.append("\nStep 1: Precedence Graph (text)")
        for name, _iv, preds in tasks:
            if preds:
                out.append(f"{', '.join(preds)} → {name}")

        # گام 2: cycle time
        out.append("\nStep 2: Cycle Time Calculation")
        cycle_interval = None
        if cycle_low and cycle_up:
            cycle_interval = (float(cycle_low), float(cycle_up))
            out.append(f"Cycle time (given): {cycle_interval}")
        elif demand_low and demand_up and access_low and access_up:
            try:
                a_low, a_up = float(access_low), float(access_up)
                d_low, d_up = float(demand_low), float(demand_up)
                c_low = round(a_low / d_up, 6)
                c_up = round(a_up / d_low, 6)
                cycle_interval = (c_low, c_up)
                out.append(f"Cycle time (calculated): {cycle_interval}")
            except Exception as e:
                out.append(f"⚠️ Error calculating cycle time: {e}")
                self._write_out(out); return
        else:
            out.append("⚠️ Please enter either Cycle time OR Demand with Access time")
            self._write_out(out); return

        # مقایسه‌ها مثل قبل
        grey_times = [iv for (_n, iv, _p) in tasks]
        all_intervals = [cycle_interval] + grey_times

        comparator = GreyNumberBatchComparator(all_intervals)
        out.append("\nPossibility Degree Method:")
        out.append(comparator.compare_all_pairs())

        mra = MinimaxRegretApproach(all_intervals)
        sorted_indices, ranks = mra.rank_numbers()
        out.append("\nRegret Approach Ranking:")
        for idx in sorted_indices:
            out.append(f"Index {idx} → {all_intervals[idx]} with rank {ranks[idx]}")

        best_idx = sorted_indices[0]
        best_cycle = all_intervals[best_idx]
        self.final_cycle_time = best_cycle
        out.append(f"\n⚡ Selected Cycle Time (Regret): {best_cycle}")

        # کران پایین گسسته (LB_set)
        T_tot = (0.0, 0.0)
        for _, iv, _ in tasks:
            T_tot = grey_add(T_tot, iv)  # جمع خاکستری
        # تقسیم خاکستری T_tot / C*
        LB_iv = grey_divide(T_tot, best_cycle)
        LB_min = math.ceil(LB_iv[0])
        LB_max = math.ceil(LB_iv[1])
        LB_set = list(range(LB_min, LB_max + 1))
        out.append("\nLower-bound on stations:")
        out.append(f"T_tot = {T_tot}")
        out.append(f"LB = T_tot ÷ C* = {LB_iv}  ⇒  LB_set = {LB_set} (LB_min={LB_min})")

        # اجرای K iteration با رهگیری بهترین
        out.append("\nStep 3: COMSOL Iterations")
        best_count = None
        best_layouts = []  # [(iter_idx, stations_layout)]
        ran_iters = 0

        for j in range(1, K + 1):
            ran_iters = j
            random.seed(j)  # انتخاب تصادفی تکرارپذیر
            stations, logs = self._run_one_iteration(tasks, best_cycle, seed=j)
            count = len(stations)

            out.append(f"\nIteration {j} (seed={j})")
            out.extend(logs)
            out.append(f"Assignment summary (stations = {count}):")
            for idx, st in enumerate(stations, start=1):
                out.append(f"  Station {idx} → {st}")

            # به‌روزرسانی بهترین تا اینجا
            if (best_count is None) or (count < best_count):
                best_count = count
                best_layouts = [(j, stations)]
            elif count == best_count:
                best_layouts.append((j, stations))

            out.append(f"Best so far after iteration {j}: {best_count} station(s).")

            # توقف زودهنگام اگر به LB_min برسیم
            if best_count == LB_min:
                out.append(f"Early stop: reached LB_min = {LB_min} at iteration {j}.")
                break

        # نتیجه نهایی
        out.append("\nFinal Result")
        out.append("-------------")
        out.append(f"Target iterations = {K}. Ran = {ran_iters}.")
        out.append(f"Best station count observed = {best_count}.")
        out.append("All best assignments (iteration → layout):")
        for it_idx, stns in best_layouts:
            out.append(f"  Iteration {it_idx} → {len(stns)} stations")
            for sidx, st in enumerate(stns, start=1):
                out.append(f"    Station {sidx} → {st}")

        # (اختیاری) محاسبه Efficiency و Balance Delay برای بهترین تعداد ایستگاه
        if best_count and best_cycle:
            T_st = grey_multiply((best_count, best_count), best_cycle)  # [k,k] × C*
            Eff = grey_divide(T_tot, T_st)
            # BD = 1 - Eff  (به صورت بازه: [1,1] - Eff)
            BD = grey_subtract((1.0, 1.0), Eff)
            out.append("\nStep 4: Efficiency and Balance Delay (based on best station count)")
            out.append(f"Total Task Time: {T_tot}")
            out.append(f"Station Time: {T_st}")
            out.append(f"Efficiency: {Eff}")
            out.append(f"Balance Delay: {BD}")

        # نوشتن خروجی در ویجت (قابل کپی)
        self._write_out(out)

    def _run_one_iteration(self, tasks, Cstar, seed=1):
        """
        اجرای یک iteration از COMSOL:
        - در هر ایستگاه:
            - Available = C*
            - Available tasks = تسک‌هایی که همهٔ پیش‌نیازهایشان انجام شده
            - برای هر تسک: P = Possibility( time > Available ), Z = 0.5 - P
            - اگر هیچ Z>=0 نبود: ایستگاه را ببند
            - وگرنه تصادفی از بین Z>=0 انتخاب کن، تخصیص بده، Available = Available - time
        """
        remaining = {t[0]: {"time": t[1], "pred": list(t[2])} for t in tasks}
        stations = []
        logs = []

        while remaining:
            available = Cstar
            st_tasks = []
            logs.append(f"Station {len(stations)+1} (Available={available})")

            while True:
                avail_tasks = [name for name, info in remaining.items()
                               if all(p not in remaining for p in info["pred"])]
                logs.append(f"  Available tasks: {avail_tasks if avail_tasks else '[]'}")
                if not avail_tasks:
                    break

                # محاسبه P و Z برای هر تسک
                Z_pack = []
                for name in avail_tasks:
                    t_iv = remaining[name]["time"]
                    comp = GreyNumberBatchComparator([t_iv, available])
                    p_txt = comp.compare_all_pairs().strip()  # "Possibility (X1 > X2) = ..."
                    try:
                        P = float(p_txt.split("=")[-1].strip())
                    except:
                        P = 0.0
                    Z = 0.5 - P
                    logs.append(f"    {name}: {p_txt} | Z={Z:.6f}")
                    if Z >= 0:
                        Z_pack.append((name, Z, t_iv))

                if not Z_pack:
                    logs.append("  All Z < 0 → close station and open a new one.")
                    break

                # انتخاب تصادفی بین Z>=0
                chosen, zval, t_iv = random.choice(Z_pack)
                logs.append(f"  → Assign {chosen} (Z={zval:.6f})")
                st_tasks.append(chosen)

                # به‌روزرسانی Available با تفریق خاکستری
                new_av = grey_subtract(available, t_iv)  # [a,b] - [c,d] = [a-d, b-c]
                logs.append(f"    Available ← {available} - {t_iv} = {new_av}")
                available = new_av

                # حذف تسک از remaining
                del remaining[chosen]

            stations.append(st_tasks)

        return stations, logs

    def _write_out(self, lines):
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "\n".join(lines))

    # ---------- نمایش گراف ----------
    def show_network(self):
        G = nx.DiGraph()
        for child in self.tree.get_children():
            task, time_range, preds = self.tree.item(child, "values")
            G.add_node(task, label=f"{task}\n{time_range}")
            if preds.strip():
                for pred in preds.split(","):
                    pred = pred.strip()
                    if pred:
                        G.add_edge(pred, task)

        if not G.nodes:
            messagebox.showwarning("Warning", "No tasks to show in network.")
            return

        win = tk.Toplevel(self)
        win.title("Precedence Network")
        win.geometry("700x500")
        win.configure(bg="#2a2a2a")

        fig, ax = plt.subplots(figsize=(7, 5))
        pos = nx.spring_layout(G)
        labels = {n: f"{n}\n{G.nodes[n]['label']}" for n in G.nodes}

        nx.draw(
            G, pos, with_labels=True, labels=labels,
            node_size=2000, node_color="#a9c9ff",
            font_size=9, font_weight="bold", arrows=True, ax=ax
        )
        ax.set_title("Precedence Network", fontsize=12)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------- ذخیره / بارگذاری ----------
    def save_project(self):
        project_data = {
            "tasks": [],
            "parameters": {
                "access": [self.access_low.get(), self.access_up.get()],
                "demand": [self.demand_low.get(), self.demand_up.get()],
                "cycle":  [self.cycle_low.get(),  self.cycle_up.get()],
                "iterations": self.iter_entry.get().strip()
            },
            "result": self.result_widget.get("1.0", tk.END).strip()
        }
        for child in self.tree.get_children():
            values = self.tree.item(child, "values")
            project_data["tasks"].append({
                "task": values[0],
                "time": values[1],
                "pred": values[2],
            })

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=4)
            messagebox.showinfo("Saved", f"Project saved to {file_path}")

    def load_project(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")
            return

        # reset table
        for child in self.tree.get_children():
            self.tree.delete(child)
        # load rows
        for task in project_data.get("tasks", []):
            self.tree.insert("", "end", values=(task["task"], task["time"], task["pred"]))

        # params
        params = project_data.get("parameters", {})
        access = params.get("access", ["",""])
        demand = params.get("demand", ["",""])
        cycle  = params.get("cycle",  ["",""])
        iters  = params.get("iterations", "10")

        self.access_low.delete(0, tk.END); self.access_low.insert(0, access[0])
        self.access_up.delete(0, tk.END);  self.access_up.insert(0, access[1])
        self.demand_low.delete(0, tk.END); self.demand_low.insert(0, demand[0])
        self.demand_up.delete(0, tk.END);  self.demand_up.insert(0, demand[1])
        self.cycle_low.delete(0, tk.END);  self.cycle_low.insert(0, cycle[0])
        self.cycle_up.delete(0, tk.END);   self.cycle_up.insert(0, cycle[1])
        self.iter_entry.delete(0, tk.END); self.iter_entry.insert(0, iters)

        # result text
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, project_data.get("result", ""))

        messagebox.showinfo("Loaded", f"Project loaded from {file_path}")
