import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from grey_number_operation import grey_add, grey_subtract, grey_multiply, grey_divide
from grey_comparison import GreyNumberBatchComparator, MinimaxRegretApproach


class RankedPositionalWeightInput(tk.Frame):
    def __init__(self, parent, result_widget):
        super().__init__(parent, bg="#2a2a2a")
        self.result_widget = result_widget
        self.tasks = []
        self.selected_item = None
        self.final_cycle_time = None

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
        self.tree.column("pred", width=220)
        self.tree.pack(fill="x", pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # فرم ورود داده
        form = tk.Frame(self, bg="#2a2a2a"); form.pack(fill="x", pady=5)
        tk.Label(form, text="Task:", bg="#2a2a2a", fg="white").grid(row=0, column=0)
        self.task_entry = tk.Entry(form, width=10); self.task_entry.grid(row=0, column=1, padx=5)
        tk.Label(form, text="Lower:", bg="#2a2a2a", fg="white").grid(row=0, column=2)
        self.lower_entry = tk.Entry(form, width=7); self.lower_entry.grid(row=0, column=3, padx=2)
        tk.Label(form, text="Upper:", bg="#2a2a2a", fg="white").grid(row=0, column=4)
        self.upper_entry = tk.Entry(form, width=7); self.upper_entry.grid(row=0, column=5, padx=2)
        tk.Label(form, text="Predecessors (comma-separated):", bg="#2a2a2a", fg="white").grid(row=0, column=6)
        self.pred_entry = tk.Entry(form, width=28); self.pred_entry.grid(row=0, column=7, padx=5)

        # دکمه‌های مدیریت تسک
        btns = tk.Frame(self, bg="#2a2a2a"); btns.pack(fill="x", pady=5)
        self.add_btn = tk.Button(btns, text="Add Task", command=self.add_task); self.add_btn.pack(side="left", padx=5)
        self.update_btn = tk.Button(btns, text="Update Task", command=self.update_task, state="disabled"); self.update_btn.pack(side="left", padx=5)

        # پارامترها
        params = tk.Frame(self, bg="#2a2a2a"); params.pack(fill="x", pady=10)
        tk.Label(params, text="Total Accessible Time [a,b]:", bg="#2a2a2a", fg="white").grid(row=0, column=0, sticky="w")
        self.access_low = tk.Entry(params, width=7);  self.access_low.grid(row=0, column=1, padx=2)
        self.access_up  = tk.Entry(params, width=7);  self.access_up.grid(row=0, column=2, padx=2)
        tk.Label(params, text="Total Demand [a,b]:", bg="#2a2a2a", fg="white").grid(row=1, column=0, sticky="w")
        self.demand_low = tk.Entry(params, width=7); self.demand_low.grid(row=1, column=1, padx=2)
        self.demand_up  = tk.Entry(params, width=7); self.demand_up.grid(row=1, column=2, padx=2)
        tk.Label(params, text="Cycle Time [a,b]:", bg="#2a2a2a", fg="white").grid(row=2, column=0, sticky="w")
        self.cycle_low = tk.Entry(params, width=7);  self.cycle_low.grid(row=2, column=1, padx=2)
        self.cycle_up  = tk.Entry(params, width=7);  self.cycle_up.grid(row=2, column=2, padx=2)

        # قفل متقابل Demand/Cycle
        self.demand_low.bind("<KeyRelease>", self.toggle_cycle_inputs)
        self.demand_up.bind("<KeyRelease>", self.toggle_cycle_inputs)
        self.cycle_low.bind("<KeyRelease>", self.toggle_demand_inputs)
        self.cycle_up.bind("<KeyRelease>", self.toggle_demand_inputs)

        # دکمه‌های اصلی
        btn_frame = tk.Frame(self, bg="#2a2a2a"); btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Run RPW", command=self.run_algorithm).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Show Network", command=self.show_network).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save Project", command=self.save_project).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Load Project", command=self.load_project).pack(side="left", padx=5)

    # ---------- جدول ----------
    def add_task(self):
        task = self.task_entry.get().strip()
        lower = self.lower_entry.get().strip()
        upper = self.upper_entry.get().strip()
        preds = self.pred_entry.get().strip()
        if not task or not lower or not upper:
            messagebox.showerror("Error", "Task and both bounds are required"); return
        try:
            low_val = float(lower); up_val = float(upper)
            if low_val > up_val:
                messagebox.showerror("Error", "Upper bound must be ≥ Lower bound"); return
        except ValueError:
            messagebox.showerror("Error", "Bounds must be numeric"); return
        self.tree.insert("", "end", values=(task, f"[{low_val},{up_val}]", preds))
        if task not in self.tasks: self.tasks.append(task)
        self.clear_form()

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        self.selected_item = selected[0]
        values = self.tree.item(self.selected_item, "values")
        self.task_entry.delete(0, tk.END); self.task_entry.insert(0, values[0])
        time_range = values[1].strip("[]").split(",")
        if len(time_range) == 2:
            self.lower_entry.delete(0, tk.END); self.lower_entry.insert(0, time_range[0])
            self.upper_entry.delete(0, tk.END); self.upper_entry.insert(0, time_range[1])
        self.pred_entry.delete(0, tk.END); self.pred_entry.insert(0, values[2])
        self.update_btn.config(state="normal"); self.add_btn.config(state="disabled")

    def update_task(self):
        if not self.selected_item: return
        task = self.task_entry.get().strip()
        lower = self.lower_entry.get().strip()
        upper = self.upper_entry.get().strip()
        preds = self.pred_entry.get().strip()
        if not task or not lower or not upper:
            messagebox.showerror("Error", "Task and both bounds are required"); return
        try:
            low_val = float(lower); up_val = float(upper)
            if low_val > up_val:
                messagebox.showerror("Error", "Upper bound must be ≥ Lower bound"); return
        except ValueError:
            messagebox.showerror("Error", "Bounds must be numeric"); return
        self.tree.item(self.selected_item, values=(task, f"[{low_val},{up_val}]", preds))
        if task not in self.tasks: self.tasks.append(task)
        self.clear_form()
        self.update_btn.config(state="disabled"); self.add_btn.config(state="normal")
        self.selected_item = None

    def clear_form(self):
        self.task_entry.delete(0, tk.END)
        self.lower_entry.delete(0, tk.END)
        self.upper_entry.delete(0, tk.END)
        self.pred_entry.delete(0, tk.END)

    def toggle_cycle_inputs(self, event=None):
        if self.demand_low.get() or self.demand_up.get():
            self.cycle_low.config(state="disabled"); self.cycle_up.config(state="disabled")
        else:
            self.cycle_low.config(state="normal"); self.cycle_up.config(state="normal")

    def toggle_demand_inputs(self, event=None):
        if self.cycle_low.get() or self.cycle_up.get():
            self.demand_low.config(state="disabled"); self.demand_up.config(state="disabled")
        else:
            self.demand_low.config(state="normal"); self.demand_up.config(state="normal")

    # ---------- ابزار RPW ----------
    def successors_of(self, task, preds_dict):
        return [t for t, preds in preds_dict.items() if task in preds]

    def compute_rpw_for_task(self, task, remaining_times, preds_dict, memo):
        if task in memo: return memo[task]
        total = tuple(remaining_times[task])
        for succ in self.successors_of(task, preds_dict):
            if succ in remaining_times:
                succ_rpw = self.compute_rpw_for_task(succ, remaining_times, preds_dict, memo)
                total = grey_add(total, succ_rpw)
        memo[task] = total
        return total

    def parse_possibility_value(self, text):
        nums = re.findall(r"([0-9]*\.?[0-9]+)", text)
        return float(nums[-1]) if nums else 0.0

    # ---------- اجرای الگوریتم ----------
    def run_algorithm(self):
        tasks = []
        grey_times = []
        preds_dict = {}
        for child in self.tree.get_children():
            values = self.tree.item(child, "values")
            tasks.append(values)
            lo, up = [float(x) for x in values[1].strip("[]").split(",")]
            grey_times.append((lo, up))
            preds = [p.strip() for p in values[2].split(",") if p.strip()]
            preds_dict[values[0]] = preds

        access_low = self.access_low.get().strip()
        access_up  = self.access_up.get().strip()
        demand_low = self.demand_low.get().strip()
        demand_up  = self.demand_up.get().strip()
        cycle_low  = self.cycle_low.get().strip()
        cycle_up   = self.cycle_up.get().strip()

        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "📊 Ranked Positional Weight (RPW)\n")

        # Step 1: نمایش متنی تقدم
        self.result_widget.insert(tk.END, "\nStep 1: Precedence Graph (text)\n")
        for t in tasks:
            tname, trng, preds = t
            if preds.strip():
                self.result_widget.insert(tk.END, f"{preds} → {tname}\n")

        # Step 2: Cycle Time
        self.result_widget.insert(tk.END, "\nStep 2: Cycle Time Calculation\n")
        cycle_interval = None
        if cycle_low and cycle_up:
            cycle_interval = (float(cycle_low), float(cycle_up))
            self.result_widget.insert(tk.END, f"Cycle time (given): {cycle_interval}\n")
        elif demand_low and demand_up and access_low and access_up:
            try:
                a_low, a_up = float(access_low), float(access_up)
                d_low, d_up = float(demand_low), float(demand_up)
                c_low, c_up = grey_divide((a_low, a_up), (d_low, d_up))
                cycle_interval = (round(c_low, 3), round(c_up, 3))
                self.result_widget.insert(tk.END, f"Cycle time (calculated): {cycle_interval}\n")
            except Exception as e:
                self.result_widget.insert(tk.END, f"⚠️ Error calculating cycle time: {e}\n")
                return
        else:
            self.result_widget.insert(tk.END, "⚠️ Please enter either Cycle time OR Demand with Access time\n")
            return

        # مقایسه امکان‌پذیری + Regret برای گزارش Step2
        all_intervals = [cycle_interval] + grey_times
        comparator = GreyNumberBatchComparator(all_intervals)
        self.result_widget.insert(tk.END, "\nPossibility Degree Method:\n")
        self.result_widget.insert(tk.END, comparator.compare_all_pairs() + "\n")

        mra = MinimaxRegretApproach(all_intervals)
        sorted_indices, ranks = mra.rank_numbers()
        self.result_widget.insert(tk.END, "\nRegret Approach Ranking:\n")
        for idx in sorted_indices:
            self.result_widget.insert(tk.END, f"Index {idx} → {all_intervals[idx]} with rank {ranks[idx]}\n")

        best_idx = sorted_indices[0]
        self.final_cycle_time = all_intervals[best_idx]
        self.result_widget.insert(tk.END, f"\n⚡ Selected Cycle Time (Regret): {self.final_cycle_time}\n")

        # Step 3: تخصیص با RPW + Regret روی RPW و شرط Z
        self.result_widget.insert(tk.END, "\nStep 3: Task Assignment using RPW\n")
        stations = {}
        station_no = 1
        remaining = {t[0]: [float(x) for x in t[1].strip('[]').split(',')] for t in tasks}
        available = [self.final_cycle_time[0], self.final_cycle_time[1]]

        while remaining:
            self.result_widget.insert(tk.END, f"\nStation {station_no} (Available={tuple(available)})\n")
            assigned_here = []

            while True:
                # 1) Available Tasks
                available_tasks = [t for t in remaining if all(p not in remaining for p in preds_dict.get(t, []))]
                self.result_widget.insert(tk.END, f"Available tasks: {available_tasks}\n")
                if not available_tasks:
                    self.result_widget.insert(tk.END, "  No available tasks (precedence). Close station.\n")
                    break

                # 2) RPW برای هر تسک از مجموعه‌ی قابل تخصیص
                memo = {}
                rpw_map = {t: self.compute_rpw_for_task(t, remaining, preds_dict, memo) for t in available_tasks}
                self.result_widget.insert(tk.END, "RPW values:\n")
                for t, v in rpw_map.items():
                    self.result_widget.insert(tk.END, f"  RPW({t}) = {v}\n")

                # 3) محاسبه Z برای هر تسک: Z = 0.5 - P(Ttask > Tavailable)
                Z_map = {}
                self.result_widget.insert(tk.END, "Z values (feasibility):\n")
                for t in available_tasks:
                    t_low, t_up = remaining[t]
                    comp = GreyNumberBatchComparator([(t_low, t_up), tuple(available)])
                    txt = comp.compare_all_pairs()
                    P = self.parse_possibility_value(txt)
                    Z = 0.5 - P
                    Z_map[t] = Z
                    self.result_widget.insert(tk.END, f"  {t}: Compare {t} vs Avail {tuple(available)} → {txt.strip()} | Z={Z}\n")

                feasible = [t for t in available_tasks if Z_map[t] >= 0]
                if not feasible:
                    self.result_widget.insert(tk.END, "  All Z < 0 → close station and open a new one.\n")
                    break

                # 4) Regret Ranking روی RPWهای تسک‌های feasible
                rpw_list = [rpw_map[t] for t in feasible]
                mra_rpw = MinimaxRegretApproach(rpw_list)
                idx_sorted, ranks_rpw = mra_rpw.rank_numbers()
                self.result_widget.insert(tk.END, "RPW Regret Ranking (among feasible):\n")
                for i in idx_sorted:
                    tname = feasible[i]
                    self.result_widget.insert(tk.END, f"  {tname}: RPW={rpw_map[tname]} | rank={ranks_rpw[i]}\n")

                chosen = feasible[idx_sorted[0]]
                self.result_widget.insert(tk.END, f"  → Assign {chosen}\n")
                assigned_here.append(chosen)

                # 5) به‌روزرسانی Available با تفریق خاکستری
                t_low, t_up = remaining[chosen]
                available = list(grey_subtract(tuple(available), (t_low, t_up)))
                del remaining[chosen]
                self.result_widget.insert(tk.END, f"  New Available = {tuple(available)}\n")

                # ادامه حلقه: معیار بستن ایستگاه فقط «همه Z<0» در تکرار بعدی است.

            stations[station_no] = assigned_here
            station_no += 1
            available = [self.final_cycle_time[0], self.final_cycle_time[1]]

        # نتیجه نهایی
        self.result_widget.insert(tk.END, "\nFinal result:\n-------------\n")
        for s, lst in stations.items():
            self.result_widget.insert(tk.END, f"Station {s} → {lst}\n")

        # Step 4: Efficiency & Balance Delay
        self.result_widget.insert(tk.END, "\nStep 4: Efficiency and Balance Delay\n")
        total_task_time = (0.0, 0.0)
        for t in tasks:
            lo, up = [float(x) for x in t[1].strip("[]").split(",")]
            total_task_time = grey_add(total_task_time, (lo, up))
        station_time = grey_multiply((float(len(stations)), float(len(stations))), self.final_cycle_time)
        efficiency = grey_divide(total_task_time, station_time)
        balance_delay = (1 - efficiency[1], 1 - efficiency[0])

        self.result_widget.insert(tk.END, f"Total Task Time: {total_task_time}\n")
        self.result_widget.insert(tk.END, f"Station Time: {station_time}\n")
        self.result_widget.insert(tk.END, f"Efficiency: {efficiency}\n")
        self.result_widget.insert(tk.END, f"Balance Delay: {balance_delay}\n")

    # ---------- شبکه ----------
    def show_network(self):
        G = nx.DiGraph()
        for child in self.tree.get_children():
            task, time_range, preds = self.tree.item(child, "values")
            G.add_node(task, label=f"{task}\n{time_range}")
            if preds.strip():
                for p in preds.split(","):
                    p = p.strip()
                    if p: G.add_edge(p, task)

        if not G.nodes:
            messagebox.showwarning("Warning", "No tasks to show in network."); return

        win = tk.Toplevel(self); win.title("Precedence Network (RPW)")
        win.geometry("700x500"); win.configure(bg="#2a2a2a")

        fig, ax = plt.subplots(figsize=(7, 5))
        pos = nx.spring_layout(G)
        labels = {n: f"{n}\n{G.nodes[n]['label']}" for n in G.nodes}
        nx.draw(G, pos, with_labels=True, labels=labels,
                node_size=2000, node_color="#a9c9ff",
                font_size=9, font_weight="bold", arrows=True, ax=ax)
        ax.set_title("Precedence Network (RPW)", fontsize=12)
        canvas = FigureCanvasTkAgg(fig, master=win); canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------- ذخیره/بارگذاری ----------
    def save_project(self):
        project_data = {
            "tasks": [],
            "parameters": {
                "access": [self.access_low.get(), self.access_up.get()],
                "demand": [self.demand_low.get(), self.demand_up.get()],
                "cycle":  [self.cycle_low.get(),  self.cycle_up.get()],
            },
            "result": self.result_widget.get("1.0", tk.END).strip()
        }
        for child in self.tree.get_children():
            v = self.tree.item(child, "values")
            project_data["tasks"].append({"task": v[0], "time": v[1], "pred": v[2]})

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=4)
            messagebox.showinfo("Saved", f"Project saved to {file_path}")

    def load_project(self):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON Files", "*.json")])
        if not file_path: return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")
            return

        for child in self.tree.get_children():
            self.tree.delete(child)
        for t in project_data.get("tasks", []):
            self.tree.insert("", "end", values=(t["task"], t["time"], t["pred"]))

        access = project_data.get("parameters", {}).get("access", ["",""])
        demand = project_data.get("parameters", {}).get("demand", ["",""])
        cycle  = project_data.get("parameters", {}).get("cycle",  ["",""])
        self.access_low.delete(0, tk.END); self.access_low.insert(0, access[0])
        self.access_up.delete(0, tk.END);  self.access_up.insert(0, access[1])
        self.demand_low.delete(0, tk.END); self.demand_low.insert(0, demand[0])
        self.demand_up.delete(0, tk.END);  self.demand_up.insert(0, demand[1])
        self.cycle_low.delete(0, tk.END);  self.cycle_low.insert(0, cycle[0])
        self.cycle_up.delete(0, tk.END);   self.cycle_up.insert(0, cycle[1])

        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, project_data.get("result", ""))
        messagebox.showinfo("Loaded", f"Project loaded from {file_path}")
