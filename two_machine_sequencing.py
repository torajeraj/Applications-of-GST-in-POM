import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

from matplotlib.figure import Figure  # FIX: برای پنجرهٔ جدا
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# کلاس‌های شما (بدون تغییر)
from grey_comparison import GreyNumberBatchComparator, MinimaxRegretApproach, probability_greater
from grey_number_operation import grey_add  # برای A=a⊕b و B=b⊕c

class TwoMachineSequencingInput(tk.Frame):
    """
    Grey Johnson sequencing (two- & three-machine)
    - جدول بالا، فرم ورود پایین، Comparison method زیر فرم
    - Save / Load / Preview / Run / Gantt
    """
    def __init__(self, parent, result_widget):
        super().__init__(parent, bg="#2a2a2a")
        self.result_widget = result_widget
        self.selected_item = None
        self.sequence = None
        self.schedule_logs = None  # ("two"/"three", log_lower, log_upper, CmaxL, CmaxU)

        # ========== Jobs table (TOP) ==========
        self.tree = ttk.Treeview(
            self, columns=("job","m1","m2","m3"),
            show="headings", height=8
        )
        self.tree.heading("job", text="Job")
        self.tree.heading("m1",  text="M1 [L,U]")
        self.tree.heading("m2",  text="M2 [L,U]")
        self.tree.heading("m3",  text="M3 [L,U] (optional)")
        self.tree.column("job", width=100, anchor="center")
        self.tree.column("m1",  width=140, anchor="center")
        self.tree.column("m2",  width=140, anchor="center")
        self.tree.column("m3",  width=170, anchor="center")
        self.tree.pack(fill="x", pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # ========== Form (under the table) ==========
        form = tk.Frame(self, bg="#2a2a2a"); form.pack(fill="x", pady=6)

        tk.Label(form, text="Job:", bg="#2a2a2a", fg="white").grid(row=0, column=0, sticky="w")
        self.job_entry = tk.Entry(form, width=12); self.job_entry.grid(row=0, column=1, padx=4)

        tk.Label(form, text="M1 Lower:", bg="#2a2a2a", fg="white").grid(row=0, column=2, sticky="w")
        self.a_low = tk.Entry(form, width=10); self.a_low.grid(row=0, column=3, padx=4)
        tk.Label(form, text="M1 Upper:", bg="#2a2a2a", fg="white").grid(row=0, column=4, sticky="w")
        self.a_up  = tk.Entry(form, width=10); self.a_up.grid(row=0, column=5, padx=4)

        tk.Label(form, text="M2 Lower:", bg="#2a2a2a", fg="white").grid(row=0, column=6, sticky="w")
        self.b_low = tk.Entry(form, width=10); self.b_low.grid(row=0, column=7, padx=4)
        tk.Label(form, text="M2 Upper:", bg="#2a2a2a", fg="white").grid(row=0, column=8, sticky="w")
        self.b_up  = tk.Entry(form, width=10); self.b_up.grid(row=0, column=9, padx=4)

        tk.Label(form, text="M3 Lower:", bg="#2a2a2a", fg="white").grid(row=0, column=10, sticky="w")
        self.c_low = tk.Entry(form, width=10); self.c_low.grid(row=0, column=11, padx=4)
        tk.Label(form, text="M3 Upper:", bg="#2a2a2a", fg="white").grid(row=0, column=12, sticky="w")
        self.c_up  = tk.Entry(form, width=10); self.c_up.grid(row=0, column=13, padx=4)

        # ========== Row action buttons (under form) ==========
        row_btns = tk.Frame(self, bg="#2a2a2a"); row_btns.pack(fill="x", pady=4)
        self.add_btn = tk.Button(row_btns, text="Add task", command=self.add_task); self.add_btn.pack(side="left", padx=5)
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

        # ========== Footer actions ==========
        foot = tk.Frame(self, bg="#2a2a2a"); foot.pack(fill="x", pady=8)
        tk.Button(foot, text="Save Project", command=self.save_project).pack(side="left", padx=5)
        tk.Button(foot, text="Load Project", command=self.load_project).pack(side="left", padx=5)
        tk.Button(foot, text="Preview", command=self.preview_inputs).pack(side="left", padx=5)
        tk.Button(foot, text="Run", command=self.run).pack(side="left", padx=5)
        self.gantt_btn = tk.Button(foot, text="Gantt", state="disabled", command=self.show_gantt)
        self.gantt_btn.pack(side="left", padx=5)

    # -------------------- Table CRUD --------------------
    def on_row_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        self.selected_item = sel[0]
        job,m1,m2,m3 = self.tree.item(self.selected_item, "values")
        self.job_entry.delete(0, tk.END); self.job_entry.insert(0, job)
        def fill(pair, s):
            try:
                a,b = s.strip("[]").split(","); a=a.strip(); b=b.strip()
            except Exception: a=b=""
            pair[0].delete(0, tk.END); pair[0].insert(0, a)
            pair[1].delete(0, tk.END); pair[1].insert(0, b)
        fill((self.a_low,self.a_up), m1)
        fill((self.b_low,self.b_up), m2)
        fill((self.c_low,self.c_up), m3)
        self.update_btn.config(state="normal"); self.add_btn.config(state="disabled")

    def clear_form(self):
        """FIX: پاک‌سازی ورودی‌ها + لغو انتخاب جدول + ریست دکمه‌ها"""
        for w in [self.job_entry,self.a_low,self.a_up,self.b_low,self.b_up,self.c_low,self.c_up]:
            w.delete(0, tk.END)
        # لغو انتخاب جدول و ریست حالت دکمه‌ها
        try:
            for sel in self.tree.selection():
                self.tree.selection_remove(sel)
        except Exception:
            pass
        self.selected_item = None
        self.update_btn.config(state="disabled")
        self.add_btn.config(state="normal")




    def _parse_iv(self, Ls, Us, label):
        sL,sU = Ls.get().strip(), Us.get().strip()
        if sL=="" and sU=="": return None
        try:
            L=float(sL); U=float(sU)
            if L>U: raise ValueError
        except Exception:
            raise ValueError(f"{label}: enter numeric [L,U] with L ≤ U")
        return (L,U)

    def add_task(self):
        try:
            job = self.job_entry.get().strip()
            if not job: raise ValueError("Job name is required.")
            a = self._parse_iv(self.a_low,self.a_up,"M1")
            b = self._parse_iv(self.b_low,self.b_up,"M2")
            c = self._parse_iv(self.c_low,self.c_up,"M3")
            if a is None or b is None:
                raise ValueError("Two-machine rule: every job must have M1 and M2.")
            m1 = f"[{a[0]},{a[1]}]"; m2 = f"[{b[0]},{b[1]}]"
            m3 = "[]" if c is None else f"[{c[0]},{c[1]}]"
            self.tree.insert("", "end", values=(job, m1, m2, m3))
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Input error", str(e))

    def update_task(self):
        if not self.selected_item: return
        try:
            job = (self.job_entry.get().strip() or self.tree.item(self.selected_item,"values")[0])
            a = self._parse_iv(self.a_low,self.a_up,"M1")
            b = self._parse_iv(self.b_low,self.b_up,"M2")
            c = self._parse_iv(self.c_low,self.c_up,"M3")
            if a is None or b is None:
                raise ValueError("Two-machine rule: every job must have M1 and M2.")
            m1 = f"[{a[0]},{a[1]}]"; m2 = f"[{b[0]},{b[1]}]"
            m3 = "[]" if c is None else f"[{c[0]},{c[1]}]"
            self.tree.item(self.selected_item, values=(job,m1,m2,m3))
            self.selected_item=None; self.update_btn.config(state="disabled"); self.add_btn.config(state="normal")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Update error", str(e))

    # -------------------- Save / Load --------------------
    def save_project(self):
        data = {"tasks":[]}
        for child in self.tree.get_children():
            job,m1,m2,m3 = self.tree.item(child,"values")
            def parse(s):
                try: a,b = s.strip("[]").split(","); return (float(a),float(b))
                except Exception: return None
            a = parse(m1); b = parse(m2); c = parse(m3)
            data["tasks"].append({"job":job,"a":a,"b":b,"c":c})
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")], title="Save Project")
        if not file_path: return
        try:
            with open(file_path,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False)
            messagebox.showinfo("Saved", f"Project saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def load_project(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON","*.json")], title="Load Project")
        if not file_path: return
        try:
            with open(file_path,"r",encoding="utf-8") as f: data=json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load:\n{e}"); return
        for child in self.tree.get_children(): self.tree.delete(child)
        for t in data.get("tasks",[]):
            job=t.get("job",""); a=t.get("a"); b=t.get("b"); c=t.get("c")
            m1="[]" if not a else f"[{a[0]},{a[1]}]"
            m2="[]" if not b else f"[{b[0]},{b[1]}]"
            m3="[]" if not c else f"[{c[0]},{c[1]}]"
            self.tree.insert("", "end", values=(job,m1,m2,m3))
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "Project loaded. Use Preview or Run.\n")

    # -------------------- Preview --------------------
    def preview_inputs(self):
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, f"Comparison method: {self.cmp_var.get() or '(not selected)'}\n\n")
        self.result_widget.insert(tk.END, "Jobs:\n")
        if not self.tree.get_children():
            self.result_widget.insert(tk.END, "  (no tasks)\n"); return
        for child in self.tree.get_children():
            job,m1,m2,m3 = self.tree.item(child,"values")
            self.result_widget.insert(tk.END, f"  - {job}: M1={m1}, M2={m2}, M3={m3}\n")

    # -------------------- Core: ranking --------------------
    def _possibility_rank(self, intervals, labels):
        """
        رتبه‌بندی اکثریت جفتی با P(Xi > Xj) — با GreyNumber واقعی نه tuple
        """
        comp = GreyNumberBatchComparator(intervals)  # → comp.numbers = list[GreyNumber]
        gn = comp.numbers

        n = len(gn)
        P = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i==j: continue
                # FIX: مقایسهٔ جفتی روی GreyNumber ها (نه تاپل)
                P[i][j] = probability_greater(gn[i], gn[j])

        report = "Pairwise P(Xi > Xj):\n"
        report += "      " + "  ".join([f"{labels[j]:>8}" for j in range(n)]) + "\n"
        for i in range(n):
            row = " " + f"{labels[i]:>6} "
            for j in range(n):
                row += ("   ----" if i==j else f"  {P[i][j]:.3f}")
            report += row + "\n"

        # اکثریت: Xi «کوچکتر» است وقتی P(Xi > Xj) < 0.5
        wins = []
        for i in range(n):
            w = sum(1 for j in range(n) if i!=j and P[i][j] < 0.5)
            wins.append((w,i))
        # بیشترین wins → «کوچک‌تر» و جلوتر
        order = [i for _,i in sorted(wins, key=lambda x: (-x[0], x[1]))]
        return order, report

    def _regret_rank(self, intervals):
        m = MinimaxRegretApproach(intervals)
        idx_order, ranks = m.rank_numbers()
        order = list(reversed(list(idx_order)))  # smallest-first
        return order, ranks

    # -------------------- Johnson step --------------------
    def _collect_jobs(self):
        jobs=[]
        for child in self.tree.get_children():
            job,m1,m2,m3 = self.tree.item(child,"values")
            def parse(s):
                try: a,b = s.strip("[]").split(","); return (float(a),float(b))
                except Exception: return None
            jobs.append({"name":job,"a":parse(m1),"b":parse(m2),"c":parse(m3)})
        return jobs

    def _validate_jobs(self, jobs):
        if not jobs: raise ValueError("Enter at least one job.")
        if not all(j["a"] and j["b"] for j in jobs):
            raise ValueError("Two-machine rule: all jobs must have M1 and M2.")
        has_c = [j["c"] is not None for j in jobs]
        if any(has_c) and not all(has_c):
            raise ValueError("Either all jobs have M3 or none (no mixing).")
        return "three" if all(has_c) else "two"

    def _johnson_step(self, remaining, pair_ab, method):
        cand=[]; labels=[]
        for j in remaining:
            for m in ("a","b"):
                iv = pair_ab[j][m]
                lab = f"{j}-{'M1' if m=='a' else 'M2'}"
                cand.append((j,m,iv,lab)); labels.append(lab)
        intervals = [x[2] for x in cand]

        text = "Candidates this step:\n"
        for (j,m,iv,lab) in cand:
            text += f"  {lab}: [{iv[0]},{iv[1]}]\n"

        if method=="possibility":
            order, matrix_txt = self._possibility_rank(intervals, labels)
            text += "\n" + matrix_txt
            text += "\nRanking by pairwise majority (ascending target):\n"
            for k in order: text += f"  {labels[k]}\n"
            k_best = order[0]
        else:
            order, ranks = self._regret_rank(intervals)
            text += "\nRegret ranking (ascending target):\n"
            for pos,k in enumerate(order,1):
                text += f"  {pos}. {labels[k]}\n"
            k_best = order[0]

        j_best, m_best, iv_best, lab_best = cand[k_best]
        return (j_best, m_best, iv_best, lab_best, text)

    def _run_johnson(self, jobs, method):
        three = all(j["c"] is not None for j in jobs)
        pair = {}
        if three:
            for j in jobs:
                pair[j["name"]] = {"a": grey_add(j["a"], j["b"]), "b": grey_add(j["b"], j["c"])}
        else:
            for j in jobs:
                pair[j["name"]] = {"a": j["a"], "b": j["b"]}

        remaining = [j["name"] for j in jobs]
        Left, Right, step_log = [], [], []

        while remaining:
            j_best, m_best, iv_best, lab_best, txt = self._johnson_step(remaining, pair, method)
            if m_best == "a":
                Left.append(j_best); place_txt = "Left"
            else:
                Right.insert(0, j_best); place_txt = "Right(front)"

            # نمایش توالی به‌شکل خواسته‌شده
            left_str  = ",".join(Left)  if Left  else ""
            right_str = ",".join(Right) if Right else ""
            seq_line = f"{left_str}........{right_str}"

            gtxt  = txt + f"\nCHOSEN {lab_best}  with interval [{iv_best[0]},{iv_best[1]}]  → place to {place_txt}\n"
            gtxt += f"SEQUNCING IN THIS Step -->  {seq_line}\n"
            step_log.append(gtxt)

            remaining.remove(j_best)

        final_seq = Left + Right
        return final_seq, step_log, ("three" if three else "two")

    # -------------------- Scheduling --------------------
    def _schedule_two(self, seq, jobs, scenario="lower"):
        log=[]; m1_end=m2_end=0.0
        for jname in seq:
            job = next(x for x in jobs if x["name"]==jname)
            a = job["a"][0] if scenario=="lower" else job["a"][1]
            b = job["b"][0] if scenario=="lower" else job["b"][1]
            s1=m1_end; e1=s1+a
            s2=max(m2_end,e1); e2=s2+b
            m1_end,m2_end = e1,e2
            log.append((jname, s1,e1,s2,e2))
        return log, m2_end

    def _schedule_three(self, seq, jobs, scenario="lower"):
        log=[]; m1_end=m2_end=m3_end=0.0
        for jname in seq:
            job = next(x for x in jobs if x["name"]==jname)
            a = job["a"][0] if scenario=="lower" else job["a"][1]
            b = job["b"][0] if scenario=="lower" else job["b"][1]
            c = job["c"][0] if scenario=="lower" else job["c"][1]
            s1=m1_end; e1=s1+a
            s2=max(m2_end,e1); e2=s2+b
            s3=max(m3_end,e2); e3=s3+c
            m1_end,m2_end,m3_end = e1,e2,e3
            log.append((jname, s1,e1,s2,e2,s3,e3))
        return log, m3_end

    # -------------------- Gantt (return Figure) --------------------
    def _gantt_two_fig(self, log, title):
        fig = Figure(figsize=(8.8, 2.6))
        ax = fig.add_subplot(111)
        for (j,s1,e1,s2,e2) in log:
            ax.barh(2, e1-s1, left=s1)
            ax.text((s1+e1)/2, 2, j, va='center', ha='center', fontsize=8)
            ax.barh(1, e2-s2, left=s2)
            ax.text((s2+e2)/2, 1, j, va='center', ha='center', fontsize=8)
        ax.set_yticks([1,2]); ax.set_yticklabels(['M2','M1'])
        ax.set_xlabel('Time'); ax.set_title(title); ax.grid(True, axis='x')
        fig.tight_layout()
        return fig

    def _gantt_three_fig(self, log, title):
        fig = Figure(figsize=(8.8, 3.4))
        ax = fig.add_subplot(111)
        for (j,s1,e1,s2,e2,s3,e3) in log:
            ax.barh(3, e1-s1, left=s1)
            ax.text((s1+e1)/2, 3, j, va='center', ha='center', fontsize=8)
            ax.barh(2, e2-s2, left=s2)
            ax.text((s2+e2)/2, 2, j, va='center', ha='center', fontsize=8)
            ax.barh(1, e3-s3, left=s3)
            ax.text((s3+e3)/2, 1, j, va='center', ha='center', fontsize=8)
        ax.set_yticks([1,2,3]); ax.set_yticklabels(['M3','M2','M1'])
        ax.set_xlabel('Time'); ax.set_title(title); ax.grid(True, axis='x')
        fig.tight_layout()
        return fig

    # -------------------- Run + Gantt --------------------
    def run(self):
        try:
            if self.cmp_var.get() not in ("possibility","regret"):
                messagebox.showwarning("Missing", "Select a comparison method (Regret / Possibility).")
                return
            jobs = self._collect_jobs()
            kind = self._validate_jobs(jobs)  # 'two' یا 'three'

            seq, logs, three_flag = self._run_johnson(jobs, self.cmp_var.get())
            self.sequence = seq

            self.result_widget.delete("1.0", tk.END)
            self.result_widget.insert(tk.END, f"Final result: {seq}\n\n")
            for i, txt in enumerate(logs, 1):
                self.result_widget.insert(tk.END, f"--- Step {i} ---\n{txt}\n")

            if three_flag == "two":
                L, CmaxL = self._schedule_two(seq, jobs, scenario="lower")
                U, CmaxU = self._schedule_two(seq, jobs, scenario="upper")
                self.schedule_logs = ("two", L, U, CmaxL, CmaxU)
            else:
                L, CmaxL = self._schedule_three(seq, jobs, scenario="lower")
                U, CmaxU = self._schedule_three(seq, jobs, scenario="upper")
                self.schedule_logs = ("three", L, U, CmaxL, CmaxU)

            self.result_widget.insert(tk.END, f"Makespan (lower bounds): {CmaxL}\n")
            self.result_widget.insert(tk.END, f"Makespan (upper bounds): {CmaxU}\n")
            self.gantt_btn.config(state="normal")

        except Exception as e:
            messagebox.showerror("Run Error", str(e))

    def show_gantt(self):
        if not self.schedule_logs:
            messagebox.showwarning("Warning","Run the algorithm first."); return
        kind, L, U, CmaxL, CmaxU = self.schedule_logs

        # FIX: پنجرهٔ جداگانهٔ Tk، نه plt.show()
        win = tk.Toplevel(self)
        win.title("Gantt Charts")
        win.geometry("980x800")
        top = tk.Frame(win); top.pack(side="top", fill="both", expand=True)

        if kind=="two":
            fig1 = self._gantt_two_fig(L, f"Two-Machine Gantt (Lower, Cmax={CmaxL})")
            fig2 = self._gantt_two_fig(U, f"Two-Machine Gantt (Upper, Cmax={CmaxU})")
        else:
            fig1 = self._gantt_three_fig(L, f"Three-Machine Gantt (Lower, Cmax={CmaxL})")
            fig2 = self._gantt_three_fig(U, f"Three-Machine Gantt (Upper, Cmax={CmaxU})")

        frame1 = tk.LabelFrame(top, text="Lower bounds"); frame1.pack(side="top", fill="both", expand=True, padx=6, pady=6)
        canvas1 = FigureCanvasTkAgg(fig1, master=frame1); canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        frame2 = tk.LabelFrame(top, text="Upper bounds"); frame2.pack(side="top", fill="both", expand=True, padx=6, pady=6)
        canvas2 = FigureCanvasTkAgg(fig2, master=frame2); canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)
