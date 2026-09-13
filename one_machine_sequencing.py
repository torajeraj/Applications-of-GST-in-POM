# one_machine_sequencing.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

from grey_number_operation import grey_add, grey_subtract, grey_divide  # ضرب لازم نیست اینجا
from grey_comparison import GreyNumberBatchComparator, MinimaxRegretApproach


class OneMachineSequencingInput(tk.Frame):
    """
    One-machine Sequencing
    - UI ورود داده (مثل قبل) + Save/Load
    - دکمه Run: اجرای FCFS, SPT, LPT, EDD, WSPT, CR, LST (هر کدام که تیک خورده)
    - مقایسه‌ی خاکستری فقط با دو روش شما: Possibility / Regret
    """

    def __init__(self, parent, result_widget):
        super().__init__(parent, bg="#2a2a2a")
        self.result_widget = result_widget
        self.selected_item = None

        # ========== Tasks table ==========
        self.tree = ttk.Treeview(
            self,
            columns=("job", "entry", "ptime", "due", "weight"),
            show="headings",
            height=8
        )
        self.tree.heading("job", text="Job")
        self.tree.heading("entry", text="Entry")
        self.tree.heading("ptime", text="Process time [a,b]")
        self.tree.heading("due", text="Due date (crisp)")
        self.tree.heading("weight", text="Weight (crisp)")

        self.tree.column("job", width=90, anchor="center")
        self.tree.column("entry", width=70, anchor="center")
        self.tree.column("ptime", width=150, anchor="center")
        self.tree.column("due", width=120, anchor="center")
        self.tree.column("weight", width=120, anchor="center")
        self.tree.pack(fill="x", pady=6)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # ========== Form row ==========
        form = tk.Frame(self, bg="#2a2a2a")
        form.pack(fill="x", pady=6)

        tk.Label(form, text="Job:", bg="#2a2a2a", fg="white").grid(row=0, column=0, sticky="w")
        self.job_entry = tk.Entry(form, width=10)
        self.job_entry.grid(row=0, column=1, padx=4)

        tk.Label(form, text="Entry #:", bg="#2a2a2a", fg="white").grid(row=0, column=2, sticky="w")
        self.entry_num = tk.Entry(form, width=8)
        self.entry_num.grid(row=0, column=3, padx=4)

        tk.Label(form, text="p lower:", bg="#2a2a2a", fg="white").grid(row=0, column=4, sticky="w")
        self.p_low = tk.Entry(form, width=8)
        self.p_low.grid(row=0, column=5, padx=4)

        tk.Label(form, text="p upper:", bg="#2a2a2a", fg="white").grid(row=0, column=6, sticky="w")
        self.p_up = tk.Entry(form, width=8)
        self.p_up.grid(row=0, column=7, padx=4)

        tk.Label(form, text="Due date:", bg="#2a2a2a", fg="white").grid(row=0, column=8, sticky="w")
        self.due_entry = tk.Entry(form, width=10)
        self.due_entry.grid(row=0, column=9, padx=4)

        tk.Label(form, text="Weight:", bg="#2a2a2a", fg="white").grid(row=0, column=10, sticky="w")
        self.w_entry = tk.Entry(form, width=10)
        self.w_entry.grid(row=0, column=11, padx=4)

        # ========== Row action buttons ==========
        row_btns = tk.Frame(self, bg="#2a2a2a")
        row_btns.pack(fill="x", pady=4)

        self.add_btn = tk.Button(row_btns, text="Add task", command=self.add_task)
        self.add_btn.pack(side="left", padx=5)

        self.update_btn = tk.Button(row_btns, text="Update task", state="disabled", command=self.update_task)
        self.update_btn.pack(side="left", padx=5)

        tk.Button(row_btns, text="Clear form", command=self.clear_form).pack(side="left", padx=5)

        # ========== Comparison method ==========
        block_cmp = tk.LabelFrame(self, text="Comparison method", bg="#2a2a2a", fg="white")
        block_cmp.pack(fill="x", pady=8)

        self.cmp_var = tk.StringVar(value="")
        tk.Radiobutton(block_cmp, text="Regret method", variable=self.cmp_var, value="regret",
                       bg="#2a2a2a", fg="white", selectcolor="#2a2a2a", activebackground="#2a2a2a").pack(side="left", padx=10, pady=4)
        tk.Radiobutton(block_cmp, text="Possibility method", variable=self.cmp_var, value="possibility",
                       bg="#2a2a2a", fg="white", selectcolor="#2a2a2a", activebackground="#2a2a2a").pack(side="left", padx=10, pady=4)

        # ========== Methods selection ==========
        block_methods = tk.LabelFrame(self, text="Method sequencing (select one or more)", bg="#2a2a2a", fg="white")
        block_methods.pack(fill="x", pady=6)

        self.fcfs_var = tk.BooleanVar(value=False)
        self.spt_var  = tk.BooleanVar(value=False)
        self.lpt_var  = tk.BooleanVar(value=False)
        self.edd_var  = tk.BooleanVar(value=False)
        self.wspt_var = tk.BooleanVar(value=False)
        self.cr_var   = tk.BooleanVar(value=False)
        self.lst_var  = tk.BooleanVar(value=False)

        for txt, var in [
            ("FCFS (first come, first serve)", self.fcfs_var),
            ("SPT (shortest process time)", self.spt_var),
            ("LPT (longest process time)", self.lpt_var),
            ("EDD (earliest due date)", self.edd_var),
            ("WSPT (Smith's rule)", self.wspt_var),
            ("CR (Critical Ratio)", self.cr_var),
            ("LST (Least Slack Time)", self.lst_var),
        ]:
            tk.Checkbutton(block_methods, text=txt, variable=var,
                           bg="#2a2a2a", fg="white", activebackground="#2a2a2a",
                           selectcolor="#2a2a2a").pack(side="left", padx=10, pady=3)

        # ========== Result metric ==========
        block_metric = tk.LabelFrame(self, text="Comparing sequencing result based on:", bg="#2a2a2a", fg="white")
        block_metric.pack(fill="x", pady=8)

        self.metric_var = tk.StringVar(value="")
        tk.Radiobutton(block_metric, text="Total grey completion time", variable=self.metric_var, value="sumC",
                       bg="#2a2a2a", fg="white", selectcolor="#2a2a2a", activebackground="#2a2a2a").pack(side="left", padx=10, pady=4)
        tk.Radiobutton(block_metric, text="Total grey delay", variable=self.metric_var, value="sumT",
                       bg="#2a2a2a", fg="white", selectcolor="#2a2a2a", activebackground="#2a2a2a").pack(side="left", padx=10, pady=4)
        tk.Radiobutton(block_metric, text="Number of tasks with delay", variable=self.metric_var, value="#tardy",
                       bg="#2a2a2a", fg="white", selectcolor="#2a2a2a", activebackground="#2a2a2a").pack(side="left", padx=10, pady=4)

        # ========== Footer actions ==========
        foot = tk.Frame(self, bg="#2a2a2a")
        foot.pack(fill="x", pady=8)

        tk.Button(foot, text="Save Project", command=self.save_project).pack(side="left", padx=5)
        tk.Button(foot, text="Load Project", command=self.load_project).pack(side="left", padx=5)
        tk.Button(foot, text="Preview inputs", command=self.preview_inputs).pack(side="left", padx=5)
        tk.Button(foot, text="Run", command=self.run_all).pack(side="left", padx=5)  # ← NEW

    # ------------------------
    # Helpers: comparators & arithmetic
    # ------------------------
    def _possibility_report(self, intervals, labels):
        """Return textual pairwise Possibility report for the given intervals."""
        comp = GreyNumberBatchComparator(intervals)
        text = comp.compare_all_pairs()
        # Add a legend Xk -> label
        legend = "\n".join([f"X{i+1} → {labels[i]} {intervals[i]}" for i in range(len(labels))])
        return f"{legend}\n{text}"

    def _regret_rank(self, intervals, order="asc"):
        """Return indices sorted by regret rank. order='asc' smallest-first, 'desc' largest-first."""
        m = MinimaxRegretApproach(intervals)
        sorted_indices, ranks = m.rank_numbers()
        order_list = list(sorted_indices)
        if order == "asc":
            order_list = list(reversed(order_list))
        return order_list, ranks

    def _sum_grey(self, intervals):
        """Grey sum of a list of [lo,hi] ranges; empty -> [0,0]."""
        total = (0.0, 0.0)
        for g in intervals:
            total = grey_add(total, g)
        return total

    def _tardy_count_and_sumT(self, C_list, jobs):
        """Given C_j (grey) and jobs list with due date d, compute #tardy, ΣT."""
        tardy = 0
        T_list = []
        for C, j in zip(C_list, jobs):
            d = j["due"]
            L = grey_subtract(C, (d, d))
            # Possibility(L > 0)
            P = self._possibility_value(L, (0.0, 0.0))
            T = (max(L[0], 0.0), max(L[1], 0.0))
            if P > 0:
                tardy += 1
            T_list.append(T)
        return tardy, self._sum_grey(T_list)

    def _possibility_value(self, A, B):
        """Extract numeric Possibility(A>B) from comparator text with exactly two intervals."""
        txt = GreyNumberBatchComparator([A, B]).compare_all_pairs()
        try:
            return float(txt.split("=")[-1].strip())
        except Exception:
            return 0.0

    def _compute_completion_times(self, sequence):
        """Compute grey completion times list C_j for a sequence of jobs (each has p=[a,b])."""
        C_list = []
        t = (0.0, 0.0)
        for j in sequence:
            t = grey_add(t, j["p"])
            C_list.append(t)
        return C_list

    # ------------------------
    # Build sequences per method
    # ------------------------
    def seq_FCFS(self, jobs):
        return sorted(jobs, key=lambda x: x["entry"])

    def seq_SPT(self, jobs):
        # Rank p_j ascending via Regret
        intervals = [j["p"] for j in jobs]
        order, _ = self._regret_rank(intervals, order="asc")
        return [jobs[i] for i in order]

    def seq_LPT(self, jobs):
        intervals = [j["p"] for j in jobs]
        order, _ = self._regret_rank(intervals, order="desc")
        return [jobs[i] for i in order]

    def seq_EDD(self, jobs):
        return sorted(jobs, key=lambda x: x["due"])

    def seq_WSPT(self, jobs):
        # r_j = p_j / [w,w]
        ratios = [grey_divide(j["p"], (j["w"], j["w"])) for j in jobs]
        order, _ = self._regret_rank(ratios, order="asc")
        return [jobs[i] for i in order]

    def seq_CR(self, jobs):
        remaining = jobs[:]
        seq = []
        t = (0.0, 0.0)
        while remaining:
            CRs = [grey_divide((j["due"], j["due"]), j["p"]) for j in [{"due": j["due"] - 0.0, "p": grey_subtract(j["p"], (0.0, 0.0))} for j in remaining]]  # no-op to keep type
            # دقیق: CR = ([d,d] - t) / p
            CRs = [grey_divide(grey_subtract((j["due"], j["due"]), t), j["p"]) for j in remaining]
            order, _ = self._regret_rank(CRs, order="desc")  # بزرگتر بهتر
            chosen = remaining[order[0]]
            seq.append(chosen)
            t = grey_add(t, chosen["p"])
            remaining.pop(order[0])
        return seq

    def seq_LST(self, jobs):
        remaining = jobs[:]
        seq = []
        t = (0.0, 0.0)
        while remaining:
            slacks = [grey_subtract(grey_subtract((j["due"], j["due"]), t), j["p"]) for j in remaining]
            order, _ = self._regret_rank(slacks, order="asc")  # کوچکتر بهتر
            chosen = remaining[order[0]]
            seq.append(chosen)
            t = grey_add(t, chosen["p"])
            remaining.pop(order[0])
        return seq

    # ------------------------
    # UI table row handlers (same as before)
    # ------------------------
    def add_task(self):
        job = self.job_entry.get().strip()
        entry = self.entry_num.get().strip()
        pl = self.p_low.get().strip()
        pu = self.p_up.get().strip()
        d = self.due_entry.get().strip()
        w = self.w_entry.get().strip()

        if not job:
            messagebox.showerror("Input error", "Job is required.")
            return
        if not entry:
            messagebox.showerror("Input error", "Entry number is required.")
            return

        try:
            entry_i = int(entry)
        except ValueError:
            messagebox.showerror("Input error", "Entry number must be an integer.")
            return

        try:
            pl_v = float(pl); pu_v = float(pu)
            if pl_v > pu_v:
                messagebox.showerror("Input error", "p lower must be ≤ p upper.")
                return
        except ValueError:
            messagebox.showerror("Input error", "p lower/upper must be numeric.")
            return

        try:
            d_v = float(d)
            if d_v < 0:
                messagebox.showerror("Input error", "Due date must be nonnegative.")
                return
        except ValueError:
            messagebox.showerror("Input error", "Due date must be numeric.")
            return

        try:
            w_v = float(w)
            if w_v <= 0:
                messagebox.showerror("Input error", "Weight must be positive.")
                return
        except ValueError:
            messagebox.showerror("Input error", "Weight must be numeric.")
            return

        self.tree.insert("", "end", values=(job, entry_i, f"[{pl_v},{pu_v}]", d_v, w_v))
        self.clear_form()

    def on_row_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_item = sel[0]
        job, entry, pstr, d, w = self.tree.item(self.selected_item, "values")

        self.job_entry.delete(0, tk.END); self.job_entry.insert(0, job)
        self.entry_num.delete(0, tk.END); self.entry_num.insert(0, entry)

        try:
            a, b = pstr.strip("[]").split(",")
        except Exception:
            a, b = "", ""
        self.p_low.delete(0, tk.END); self.p_low.insert(0, a)
        self.p_up.delete(0, tk.END); self.p_up.insert(0, b)

        self.due_entry.delete(0, tk.END); self.due_entry.insert(0, d)
        self.w_entry.delete(0, tk.END); self.w_entry.insert(0, w)

        self.update_btn.config(state="normal")
        self.add_btn.config(state="disabled")

    def update_task(self):
        if not self.selected_item:
            return
        job = self.job_entry.get().strip()
        entry = self.entry_num.get().strip()
        pl = self.p_low.get().strip()
        pu = self.p_up.get().strip()
        d = self.due_entry.get().strip()
        w = self.w_entry.get().strip()

        if not job:
            messagebox.showerror("Input error", "Job is required.")
            return
        try:
            entry_i = int(entry)
        except ValueError:
            messagebox.showerror("Input error", "Entry number must be integer.")
            return
        try:
            pl_v = float(pl); pu_v = float(pu)
            if pl_v > pu_v:
                messagebox.showerror("Input error", "p lower must be ≤ p upper.")
                return
        except ValueError:
            messagebox.showerror("Input error", "p lower/upper must be numeric.")
            return
        try:
            d_v = float(d); w_v = float(w)
        except ValueError:
            messagebox.showerror("Input error", "Due date/Weight must be numeric.")
            return
        if d_v < 0:
            messagebox.showerror("Input error", "Due date must be nonnegative.")
            return
        if w_v <= 0:
            messagebox.showerror("Input error", "Weight must be positive.")
            return

        self.tree.item(self.selected_item, values=(job, entry_i, f"[{pl_v},{pu_v}]", d_v, w_v))
        self.selected_item = None
        self.update_btn.config(state="disabled")
        self.add_btn.config(state="normal")
        self.clear_form()

    def clear_form(self):
        self.job_entry.delete(0, tk.END)
        self.entry_num.delete(0, tk.END)
        self.p_low.delete(0, tk.END)
        self.p_up.delete(0, tk.END)
        self.due_entry.delete(0, tk.END)
        self.w_entry.delete(0, tk.END)

    # ------------------------
    # Preview (no computation)
    # ------------------------
    def preview_inputs(self):
        if self.cmp_var.get() not in ("regret", "possibility"):
            messagebox.showwarning("Missing choice", "Select a comparison method (Regret / Possibility).")
            return

        chosen_methods = []
        if self.fcfs_var.get(): chosen_methods.append("FCFS")
        if self.spt_var.get():  chosen_methods.append("SPT")
        if self.lpt_var.get():  chosen_methods.append("LPT")
        if self.edd_var.get():  chosen_methods.append("EDD")
        if self.wspt_var.get(): chosen_methods.append("WSPT")
        if self.cr_var.get():   chosen_methods.append("CR")
        if self.lst_var.get():  chosen_methods.append("LST")
        if not chosen_methods:
            messagebox.showwarning("Missing methods", "Select at least one sequencing method.")
            return

        if self.metric_var.get() not in ("sumC", "sumT", "#tardy"):
            messagebox.showwarning("Missing metric", "Select one metric for comparing results.")
            return

        tasks = []
        for child in self.tree.get_children():
            tasks.append(self.tree.item(child, "values"))

        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "One-machine Sequencing — Input Preview\n")
        self.result_widget.insert(tk.END, f"Comparison method: {self.cmp_var.get()}\n")
        self.result_widget.insert(tk.END, f"Selected methods: {', '.join(chosen_methods)}\n")
        metric_title = {"sumC":"Total grey completion time", "sumT":"Total grey delay", "#tardy":"Number of tasks with delay"}[self.metric_var.get()]
        self.result_widget.insert(tk.END, f"Compare results based on: {metric_title}\n\n")
        self.result_widget.insert(tk.END, "Tasks:\n")
        if not tasks:
            self.result_widget.insert(tk.END, "  (no tasks entered)\n")
        else:
            for v in tasks:
                job, entry, pstr, d, w = v
                self.result_widget.insert(tk.END, f"  - {job}: Entry={entry}, p={pstr}, d={d}, w={w}\n")

    # ------------------------
    # Save / Load Project (JSON)
    # ------------------------
    def save_project(self):
        data = {
            "tasks": [],
            "settings": {
                "comparator": self.cmp_var.get(),
                "methods": {
                    "FCFS": self.fcfs_var.get(),
                    "SPT":  self.spt_var.get(),
                    "LPT":  self.lpt_var.get(),
                    "EDD":  self.edd_var.get(),
                    "WSPT": self.wspt_var.get(),
                    "CR":   self.cr_var.get(),
                    "LST":  self.lst_var.get(),
                },
                "metric": self.metric_var.get()
            }
        }

        for child in self.tree.get_children():
            job, entry, pstr, d, w = self.tree.item(child, "values")
            try:
                a, b = pstr.strip("[]").split(",")
                a = float(a); b = float(b)
            except Exception:
                a, b = None, None
            data["tasks"].append({
                "job": job,
                "entry": int(entry),
                "p": [a, b],
                "due": float(d),
                "weight": float(w),
            })

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Sequencing Project"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Saved", f"Project saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project:\n{e}")

    def load_project(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Load Sequencing Project"
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project:\n{e}")
            return

        for child in self.tree.get_children():
            self.tree.delete(child)

        for t in data.get("tasks", []):
            job = t.get("job", "")
            entry = t.get("entry", "")
            p = t.get("p", [None, None])
            d = t.get("due", "")
            w = t.get("weight", "")
            pstr = "[]" if (p[0] is None or p[1] is None) else f"[{p[0]},{p[1]}]"
            self.tree.insert("", "end", values=(job, entry, pstr, d, w))

        st = data.get("settings", {})
        self.cmp_var.set(st.get("comparator", ""))
        m = st.get("methods", {})
        self.fcfs_var.set(bool(m.get("FCFS", False)))
        self.spt_var.set(bool(m.get("SPT", False)))
        self.lpt_var.set(bool(m.get("LPT", False)))
        self.edd_var.set(bool(m.get("EDD", False)))
        self.wspt_var.set(bool(m.get("WSPT", False)))
        self.cr_var.set(bool(m.get("CR", False)))
        self.lst_var.set(bool(m.get("LST", False)))
        self.metric_var.set(st.get("metric", ""))

        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "Project loaded.\nUse 'Preview inputs' or 'Run' to proceed.\n")

    # ------------------------
    # RUN all selected methods
    # ------------------------
    def run_all(self):
        # Validate
        if self.cmp_var.get() not in ("regret", "possibility"):
            messagebox.showwarning("Missing choice", "Select a comparison method (Regret / Possibility).")
            return
        methods = []
        if self.fcfs_var.get(): methods.append("FCFS")
        if self.spt_var.get():  methods.append("SPT")
        if self.lpt_var.get():  methods.append("LPT")
        if self.edd_var.get():  methods.append("EDD")
        if self.wspt_var.get(): methods.append("WSPT")
        if self.cr_var.get():   methods.append("CR")
        if self.lst_var.get():  methods.append("LST")
        if not methods:
            messagebox.showwarning("Missing methods", "Select at least one sequencing method.")
            return
        if self.metric_var.get() not in ("sumC", "sumT", "#tardy"):
            messagebox.showwarning("Missing metric", "Select one metric for comparing results.")
            return

        jobs = []
        for child in self.tree.get_children():
            job, entry, pstr, d, w = self.tree.item(child, "values")
            try:
                a, b = pstr.strip("[]").split(",")
                p = (float(a), float(b))
            except Exception:
                messagebox.showerror("Input error", f"Bad p interval for job {job}.")
                return
            jobs.append({"job": job, "entry": int(entry), "p": p, "due": float(d), "w": float(w)})

        # Run per method
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "One-machine Sequencing — RUN\n")
        self.result_widget.insert(tk.END, f"Comparator: {self.cmp_var.get()}\n")
        self.result_widget.insert(tk.END, f"Methods: {', '.join(methods)}\n")
        self.result_widget.insert(tk.END, f"Metric for cross-method selection: {self.metric_var.get()}\n\n")

        summary = []  # collect (method, #tardy, sumT, sumC, extra)

        for M in methods:
            self.result_widget.insert(tk.END, f"=== {M} ===\n")

            # Stepwise selection log (especially for SPT/LPT/WSPT/CR/LST)
            if M == "FCFS":
                seq = self.seq_FCFS(jobs)
                self.result_widget.insert(tk.END, "Order by Entry ascending.\n")
            elif M == "EDD":
                seq = self.seq_EDD(jobs)
                self.result_widget.insert(tk.END, "Order by due date ascending.\n")
            elif M == "SPT":
                # verbose: show possibility + regret at first step across all p_j
                p_intervals = [j["p"] for j in jobs]
                if self.cmp_var.get() == "possibility":
                    self.result_widget.insert(tk.END, "Possibility report on p_j:\n")
                    self.result_widget.insert(tk.END, self._possibility_report(p_intervals, [j["job"] for j in jobs]) + "\n")
                order, ranks = self._regret_rank(p_intervals, order="asc")
                self.result_widget.insert(tk.END, "Regret ranking on p_j (ascending target):\n")
                for idx in order:
                    self.result_widget.insert(tk.END, f"  {jobs[idx]['job']} p={jobs[idx]['p']}\n")
                seq = [jobs[i] for i in order]
            elif M == "LPT":
                p_intervals = [j["p"] for j in jobs]
                if self.cmp_var.get() == "possibility":
                    self.result_widget.insert(tk.END, "Possibility report on p_j:\n")
                    self.result_widget.insert(tk.END, self._possibility_report(p_intervals, [j["job"] for j in jobs]) + "\n")
                order, ranks = self._regret_rank(p_intervals, order="desc")
                self.result_widget.insert(tk.END, "Regret ranking on p_j (descending target):\n")
                for idx in order:
                    self.result_widget.insert(tk.END, f"  {jobs[idx]['job']} p={jobs[idx]['p']}\n")
                seq = [jobs[i] for i in order]
            elif M == "WSPT":
                ratios = [grey_divide(j["p"], (j["w"], j["w"])) for j in jobs]
                if self.cmp_var.get() == "possibility":
                    self.result_widget.insert(tk.END, "Possibility report on r_j=p_j/[w,w]:\n")
                    self.result_widget.insert(tk.END, self._possibility_report(ratios, [j["job"] for j in jobs]) + "\n")
                order, ranks = self._regret_rank(ratios, order="asc")
                self.result_widget.insert(tk.END, "Regret ranking on r_j (ascending target):\n")
                for idx in order:
                    self.result_widget.insert(tk.END, f"  {jobs[idx]['job']} r={ratios[idx]}\n")
                seq = [jobs[i] for i in order]
            elif M == "CR":
                # Dynamic; show step log
                remaining = jobs[:]
                seq = []
                t = (0.0, 0.0)
                step = 1
                while remaining:
                    CRs = [grey_divide(grey_subtract((j["due"], j["due"]), t), j["p"]) for j in remaining]
                    if self.cmp_var.get() == "possibility":
                        self.result_widget.insert(tk.END, f"Step {step} — Possibility on CR:\n")
                        self.result_widget.insert(tk.END, self._possibility_report(CRs, [j["job"] for j in remaining]) + "\n")
                    order, ranks = self._regret_rank(CRs, order="desc")
                    chosen = remaining[order[0]]
                    self.result_widget.insert(tk.END, f"Step {step} — choose {chosen['job']}, CR={CRs[order[0]]}\n")
                    seq.append(chosen)
                    t = grey_add(t, chosen["p"])
                    remaining.pop(order[0])
                    step += 1
            elif M == "LST":
                remaining = jobs[:]
                seq = []
                t = (0.0, 0.0)
                step = 1
                while remaining:
                    slacks = [grey_subtract(grey_subtract((j["due"], j["due"]), t), j["p"]) for j in remaining]
                    if self.cmp_var.get() == "possibility":
                        self.result_widget.insert(tk.END, f"Step {step} — Possibility on Slack:\n")
                        self.result_widget.insert(tk.END, self._possibility_report(slacks, [j["job"] for j in remaining]) + "\n")
                    order, ranks = self._regret_rank(slacks, order="asc")
                    chosen = remaining[order[0]]
                    self.result_widget.insert(tk.END, f"Step {step} — choose {chosen['job']}, Slack={slacks[order[0]]}\n")
                    seq.append(chosen)
                    t = grey_add(t, chosen["p"])
                    remaining.pop(order[0])
                    step += 1
            else:
                seq = jobs[:]  # fallback

            # Metrics
            C_list = self._compute_completion_times(seq)
            tardy_cnt, sumT = self._tardy_count_and_sumT(C_list, seq)
            sumC = self._sum_grey(C_list)

            # Print results
            self.result_widget.insert(tk.END, "Sequence:\n")
            self.result_widget.insert(tk.END, "  " + " → ".join([j["job"] for j in seq]) + "\n")
            self.result_widget.insert(tk.END, "Completion times C_j:\n")
            for j, C in zip(seq, C_list):
                self.result_widget.insert(tk.END, f"  {j['job']}: {C}\n")
            self.result_widget.insert(tk.END, f"#Tardy = {tardy_cnt}\n")
            self.result_widget.insert(tk.END, f"ΣT = {sumT}\n")
            self.result_widget.insert(tk.END, f"ΣC = {sumC}\n\n")

            summary.append((M, tardy_cnt, sumT, sumC))

        # Cross-method comparison
        self.result_widget.insert(tk.END, "=== Cross-method comparison ===\n")
        if self.metric_var.get() == "#tardy":
            best = min(summary, key=lambda x: x[1])
            for M, tardy_cnt, sumT, sumC in summary:
                self.result_widget.insert(tk.END, f"{M}: #Tardy={tardy_cnt}\n")
            self.result_widget.insert(tk.END, f"\nBest (min #Tardy): {best[0]}\n")
        else:
            # pick by Regret among intervals
            idx = 2 if self.metric_var.get() == "sumT" else 3  # 2: sumT, 3: sumC
            intervals = [s[idx] for s in summary]
            m = MinimaxRegretApproach(intervals)
            order, ranks = m.rank_numbers()
            # smallest-first view:
            order = list(reversed(list(order)))
            for pos, oi in enumerate(order, 1):
                self.result_widget.insert(tk.END, f"{pos}. {summary[oi][0]} → {intervals[oi]} (rank={ranks[oi]})\n")
            self.result_widget.insert(tk.END, f"\nBest: {summary[order[0]][0]}\n")

