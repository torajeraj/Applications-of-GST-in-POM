# grey_aggregate_chase.py
# ------------------------------------------------------------
# Grey Aggregate Planning — Chase Strategy (finalized + regret display)
# - Candidates per period: WL=ceil(Wreq_lower), WU=ceil(Wreq_upper) (unique if equal)
# - Accept iff P(Q > D) > 0.5  → compute costs; else "Reject" (no cost)
# - Among accepted, pick MIN total cost via Minimax Regret:
#       run MRA on NEGATED costs (so "larger is better" ≡ "smaller original cost")
# - Additionally, DISPLAY the regret ranking and explicitly state:
#       "the smaller grey cost is selected"
# - If all rejected -> choose WU (forced) and compute its costs for reporting
#
# Hook in main_app.py:
#   from grey_aggregate_chase import GreyAPChaseInput
#   analysis_registry["Chase strategy"] = GreyAPChaseInput
# ------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import json
import math

# ---- comparators from your project ----
try:
    from grey_comparison import GreyNumberBatchComparator, MinimaxRegretApproach
except Exception:
    GreyNumberBatchComparator = None
    MinimaxRegretApproach = None

# ---- grey arithmetic from your project ----
try:
    from grey_number_operation import grey_add, grey_subtract, grey_multiply, grey_divide
except Exception:
    def grey_add(a, b): return (a[0] + b[0], a[1] + b[1])
    def grey_subtract(a, b): return (a[0] - b[1], a[1] - b[0])
    def grey_multiply(a, b):
        vals = [a[0]*b[0], a[0]*b[1], a[1]*b[0], a[1]*b[1]]
        return (min(vals), max(vals))
    def grey_divide(a, b):
        vals = [a[0]/b[0], a[0]/b[1], a[1]/b[0], a[1]/b[1]]
        return (min(vals), max(vals))

# ---------- utils ----------
def fmt_iv(g):
    def f(x):
        s = f"{x:.6f}".rstrip("0").rstrip(".")
        return s if s != "-0" else "0"
    return f"[{f(g[0])},{f(g[1])}]"

def parse_interval(s):
    if isinstance(s, (list, tuple)) and len(s) == 2:
        return (float(s[0]), float(s[1]))
    s = str(s).strip().strip("[]")
    lo, hi = s.split(",")
    return (float(lo), float(hi))

def possibility_x1_gt_x2(a, b):
    """Possibility(X1 > X2) via your comparator's text output."""
    if GreyNumberBatchComparator is None:
        return 0.5
    comp = GreyNumberBatchComparator([a, b])
    txt = comp.compare_all_pairs()
    for line in txt.splitlines():
        if "(X1 > X2)" in line and "=" in line:
            try:
                return float(line.split("=")[-1].strip())
            except Exception:
                return 0.5
    return 0.5

def negate_interval(g):
    """(-1) × [a,b] = [-b, -a]"""
    return (-g[1], -g[0])


class GreyAPChaseInput(tk.Frame):
    def __init__(self, parent, result_widget: ScrolledText):
        super().__init__(parent, bg="#2a2a2a")
        self.result_widget = result_widget
        self.selected_item = None

        # ===== Periods table =====
        table_frame = tk.Frame(self, bg="#2a2a2a")
        table_frame.pack(fill="x", pady=6)

        cols = ("period", "demand")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=7)
        self.tree.heading("period", text="Period")
        self.tree.heading("demand", text="Demand [a,b]")
        self.tree.column("period", width=90, anchor="center")
        self.tree.column("demand", width=140, anchor="center")
        self.tree.pack(side="left", fill="x", expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # Period inputs
        form = tk.Frame(self, bg="#2a2a2a")
        form.pack(fill="x", pady=4)

        tk.Label(form, text="Period:", bg="#2a2a2a", fg="white").grid(row=0, column=0, padx=6, pady=2, sticky="w")
        self.period_entry = tk.Entry(form, width=10)
        self.period_entry.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(form, text="Demand Lower:", bg="#2a2a2a", fg="white").grid(row=0, column=2, padx=6, pady=2, sticky="w")
        self.d_low_entry = tk.Entry(form, width=10)
        self.d_low_entry.grid(row=0, column=3, padx=4, pady=2)

        tk.Label(form, text="Demand Upper:", bg="#2a2a2a", fg="white").grid(row=0, column=4, padx=6, pady=2, sticky="w")
        self.d_up_entry = tk.Entry(form, width=10)
        self.d_up_entry.grid(row=0, column=5, padx=4, pady=2)

        btns = tk.Frame(self, bg="#2a2a2a")
        btns.pack(fill="x", pady=4)
        self.add_btn = tk.Button(btns, text="Add Period", command=self.add_period); self.add_btn.pack(side="left", padx=5)
        self.update_btn = tk.Button(btns, text="Update Period", command=self.update_period, state="disabled"); self.update_btn.pack(side="left", padx=5)
        self.clear_btn = tk.Button(btns, text="Clear Inputs", command=self.clear_inputs); self.clear_btn.pack(side="left", padx=5)

        # ===== Parameters =====
        params = tk.LabelFrame(self, text="Parameters", bg="#2a2a2a", fg="white")
        params.pack(fill="x", pady=6)

        tk.Label(params, text="Initial Workforce (W0):", bg="#2a2a2a", fg="white").grid(row=0, column=0, padx=6, pady=2, sticky="w")
        self.w0_entry = tk.Entry(params, width=10); self.w0_entry.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(params, text="Opening Inventory I0 (crisp):", bg="#2a2a2a", fg="white").grid(row=0, column=2, padx=6, pady=2, sticky="w")
        self.i0_entry = tk.Entry(params, width=10); self.i0_entry.grid(row=0, column=3, padx=4, pady=2)

        tk.Label(params, text="Opening Backorder B0 (crisp):", bg="#2a2a2a", fg="white").grid(row=0, column=4, padx=6, pady=2, sticky="w")
        self.b0_entry = tk.Entry(params, width=10); self.b0_entry.grid(row=0, column=5, padx=4, pady=2)

        tk.Label(params, text="Productivity P [a,b]:", bg="#2a2a2a", fg="white").grid(row=1, column=0, padx=6, pady=2, sticky="w")
        self.p_low_entry = tk.Entry(params, width=10); self.p_low_entry.grid(row=1, column=1, padx=4, pady=2)
        self.p_up_entry  = tk.Entry(params, width=10); self.p_up_entry.grid(row=1, column=2, padx=4, pady=2)

        # ===== Costs =====
        cost = tk.LabelFrame(self, text="Costs (per period/unit)", bg="#2a2a2a", fg="white")
        cost.pack(fill="x", pady=6)

        tk.Label(cost, text="Regular prod. cost C_reg [a,b]:", bg="#2a2a2a", fg="white").grid(row=0, column=0, padx=6, pady=2, sticky="w")
        self.creg_low = tk.Entry(cost, width=10); self.creg_low.grid(row=0, column=1, padx=4, pady=2)
        self.creg_up  = tk.Entry(cost, width=10); self.creg_up.grid(row=0, column=2, padx=4, pady=2)

        tk.Label(cost, text="Hiring cost C_hire [a,b]:", bg="#2a2a2a", fg="white").grid(row=0, column=3, padx=6, pady=2, sticky="w")
        self.chire_low = tk.Entry(cost, width=10); self.chire_low.grid(row=0, column=4, padx=4, pady=2)
        self.chire_up  = tk.Entry(cost, width=10); self.chire_up.grid(row=0, column=5, padx=4, pady=2)

        tk.Label(cost, text="Firing cost C_fire [a,b]:", bg="#2a2a2a", fg="white").grid(row=1, column=0, padx=6, pady=2, sticky="w")
        self.cfire_low = tk.Entry(cost, width=10); self.cfire_low.grid(row=1, column=1, padx=4, pady=2)
        self.cfire_up  = tk.Entry(cost, width=10); self.cfire_up.grid(row=1, column=2, padx=4, pady=2)

        tk.Label(cost, text="Personnel cost C_pers [a,b]:", bg="#2a2a2a", fg="white").grid(row=1, column=3, padx=6, pady=2, sticky="w")
        self.cpers_low = tk.Entry(cost, width=10); self.cpers_low.grid(row=1, column=4, padx=4, pady=2)
        self.cpers_up  = tk.Entry(cost, width=10); self.cpers_up.grid(row=1, column=5, padx=4, pady=2)

        # ===== Actions =====
        action = tk.Frame(self, bg="#2a2a2a")
        action.pack(fill="x", pady=6)
        tk.Button(action, text="Run (Chase)", command=self.run_planning).pack(side="left", padx=5)
        tk.Button(action, text="Save Project", command=self.save_project).pack(side="left", padx=5)
        tk.Button(action, text="Load Project", command=self.load_project).pack(side="left", padx=5)

    # ---------- table ops ----------
    def add_period(self):
        p = self.period_entry.get().strip()
        dL = self.d_low_entry.get().strip()
        dU = self.d_up_entry.get().strip()
        if not p or not dL or not dU:
            messagebox.showerror("Error", "Enter period and both demand bounds.")
            return
        try:
            dL_v = float(dL); dU_v = float(dU)
            if dL_v > dU_v:
                messagebox.showerror("Error", "Upper bound must be ≥ lower bound.")
                return
        except ValueError:
            messagebox.showerror("Error", "Demand bounds must be numeric.")
            return
        self.tree.insert("", "end", values=(p, f"[{dL_v},{dU_v}]"))
        self.clear_inputs()

    def on_row_select(self, _evt=None):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_item = sel[0]
        period, demand = self.tree.item(self.selected_item, "values")
        self.period_entry.delete(0, tk.END); self.period_entry.insert(0, period)
        try:
            lo, hi = demand.strip("[]").split(",")
            self.d_low_entry.delete(0, tk.END); self.d_low_entry.insert(0, lo)
            self.d_up_entry.delete(0, tk.END);  self.d_up_entry.insert(0, hi)
        except Exception:
            pass
        self.update_btn.config(state="normal")
        self.add_btn.config(state="disabled")

    def update_period(self):
        if not self.selected_item:
            return
        p = self.period_entry.get().strip()
        dL = self.d_low_entry.get().strip()
        dU = self.d_up_entry.get().strip()
        if not p or not dL or not dU:
            messagebox.showerror("Error", "Enter period and both demand bounds.")
            return
        try:
            dL_v = float(dL); dU_v = float(dU)
            if dL_v > dU_v:
                messagebox.showerror("Error", "Upper bound must be ≥ lower bound.")
                return
        except ValueError:
            messagebox.showerror("Error", "Demand bounds must be numeric.")
            return
        self.tree.item(self.selected_item, values=(p, f"[{dL_v},{dU_v}]"))
        self.selected_item = None
        self.update_btn.config(state="disabled")
        self.add_btn.config(state="normal")
        self.clear_inputs()

    def clear_inputs(self):
        self.period_entry.delete(0, tk.END)
        self.d_low_entry.delete(0, tk.END)
        self.d_up_entry.delete(0, tk.END)

    # ---------- planning ----------
    def run_planning(self):
        # periods
        periods = []
        for it in self.tree.get_children():
            period, demand = self.tree.item(it, "values")
            try:
                d_iv = parse_interval(demand)
            except Exception:
                messagebox.showerror("Error", f"Bad demand format at period {period}. Use [a,b].")
                return
            periods.append((period, d_iv))
        if not periods:
            messagebox.showwarning("Warning", "No periods entered.")
            return

        # params
        try:
            W_prev = int(float(self.w0_entry.get().strip()))
        except Exception:
            messagebox.showerror("Error", "Initial workforce W0 must be integer.")
            return

        try:
            I0 = float(self.i0_entry.get().strip() or "0")
            B0 = float(self.b0_entry.get().strip() or "0")
        except Exception:
            messagebox.showerror("Error", "I0 and B0 must be numeric.")
            return

        try:
            P = (float(self.p_low_entry.get().strip()), float(self.p_up_entry.get().strip()))
            if P[0] > P[1]:
                messagebox.showerror("Error", "Productivity: upper must be ≥ lower.")
                return
        except Exception:
            messagebox.showerror("Error", "Productivity P must be two numeric bounds.")
            return

        def read_cost(lo_e, up_e, name):
            try:
                lo = float(lo_e.get().strip()); up = float(up_e.get().strip())
                if lo > up: raise ValueError
                return (lo, up)
            except Exception:
                messagebox.showerror("Error", f"{name} must be two numeric bounds [a,b] with a≤b.")
                raise

        try:
            C_reg  = read_cost(self.creg_low,  self.creg_up,  "C_reg")
            C_hire = read_cost(self.chire_low, self.chire_up, "C_hire")
            C_fire = read_cost(self.cfire_low, self.cfire_up, "C_fire")
            C_pers = read_cost(self.cpers_low, self.cpers_up, "C_pers")
        except Exception:
            return

        w = self.result_widget
        w.delete("1.0", tk.END)
        w.insert(tk.END, "📦 Grey Aggregate Planning — Chase Strategy (accept iff P(Q>D)>0.5)\n")
        w.insert(tk.END, f"W0={W_prev}, I0={I0}, B0={B0}\n")
        w.insert(tk.END, f"P={fmt_iv(P)} | Costs: C_reg={fmt_iv(C_reg)}, C_hire={fmt_iv(C_hire)}, C_fire={fmt_iv(C_fire)}, C_pers={fmt_iv(C_pers)}\n")
        w.insert(tk.END, "-"*60 + "\n")

        summary_rows = []
        grand_total = (0.0, 0.0)

        for idx, (period, D_t) in enumerate(periods, start=1):
            w.insert(tk.END, f"\nPeriod {period}\n")
            w.insert(tk.END, f"Demand D_t = {fmt_iv(D_t)}\n")

            # Wreq = D/P
            Wreq = grey_divide(D_t, P)
            w.insert(tk.END, f"W_req = D_t / P = {fmt_iv(Wreq)}\n")

            WL = max(0, math.ceil(Wreq[0]))
            WU = max(0, math.ceil(Wreq[1]))
            cand_list = sorted({WL, WU})
            w.insert(tk.END, f"Candidates W (ceil lower/upper only): {cand_list}\n")

            cand_infos = []
            for Wc in cand_list:
                Qreg = grey_multiply((Wc, Wc), P)   # capacity interval
                P_q_gt_d = possibility_x1_gt_x2(Qreg, D_t)  # P(Q > D)
                if P_q_gt_d > 0.5:
                    # Accepted → compute all costs
                    cost_pers = grey_multiply((Wc, Wc), C_pers)
                    cost_reg  = grey_multiply(D_t, C_reg)   # chase: produce demand
                    hire_cnt  = max(0, Wc - W_prev)
                    fire_cnt  = max(0, W_prev - Wc)
                    cost_hire = grey_multiply((hire_cnt, hire_cnt), C_hire) if hire_cnt > 0 else (0.0, 0.0)
                    cost_fire = grey_multiply((fire_cnt, fire_cnt), C_fire) if fire_cnt > 0 else (0.0, 0.0)
                    cost_total = grey_add(grey_add(cost_pers, cost_reg), grey_add(cost_hire, cost_fire))
                    cand_infos.append({
                        "W": Wc, "Qreg": Qreg, "P_q_gt_d": P_q_gt_d, "rejected": False,
                        "cost_pers": cost_pers, "cost_reg": cost_reg,
                        "cost_hire": cost_hire, "cost_fire": cost_fire,
                        "cost_total": cost_total
                    })
                else:
                    # Reject → no cost
                    cand_infos.append({
                        "W": Wc, "Qreg": Qreg, "P_q_gt_d": P_q_gt_d, "rejected": True,
                        "cost_pers": None, "cost_reg": None, "cost_hire": None, "cost_fire": None, "cost_total": None
                    })

            # log candidates
            w.insert(tk.END, "Candidate evaluation:\n")
            for ci in cand_infos:
                if ci["rejected"]:
                    w.insert(tk.END, f"  W={ci['W']:>3} | Qreg={fmt_iv(ci['Qreg'])} | P(Q>D)={ci['P_q_gt_d']:.6f} | Reject\n")
                else:
                    w.insert(tk.END, f"  W={ci['W']:>3} | Qreg={fmt_iv(ci['Qreg'])} | P(Q>D)={ci['P_q_gt_d']:.6f} | Cost_total={fmt_iv(ci['cost_total'])}\n")

            accepted = [ci for ci in cand_infos if not ci["rejected"]]

            if not accepted:
                # forced: choose WU; compute cost for reporting
                chosen_W = WU
                Qreg = grey_multiply((chosen_W, chosen_W), P)
                hire_cnt  = max(0, chosen_W - W_prev)
                fire_cnt  = max(0, W_prev - chosen_W)
                cost_pers = grey_multiply((chosen_W, chosen_W), C_pers)
                cost_reg  = grey_multiply(D_t, C_reg)
                cost_hire = grey_multiply((hire_cnt, hire_cnt), C_hire) if hire_cnt > 0 else (0.0, 0.0)
                cost_fire = grey_multiply((fire_cnt, fire_cnt), C_fire) if fire_cnt > 0 else (0.0, 0.0)
                cost_total = grey_add(grey_add(cost_pers, cost_reg), grey_add(cost_hire, cost_fire))
                chosen = {
                    "W": chosen_W, "Qreg": Qreg, "rejected": True,
                    "cost_pers": cost_pers, "cost_reg": cost_reg,
                    "cost_hire": cost_hire, "cost_fire": cost_fire, "cost_total": cost_total
                }
                forced = True
                # نمایش توضیح
                w.insert(tk.END, "All candidates rejected → choosing W_U (forced).\n")
            else:
                # DISPLAY regret ranking on costs (minimization) and choose
                forced = False
                neg_costs = [negate_interval(ci["cost_total"]) for ci in accepted]
                if MinimaxRegretApproach is not None:
                    mra = MinimaxRegretApproach(neg_costs)
                    sorted_idx, ranks = mra.rank_numbers()
                    w.insert(tk.END, "Regret ranking on total cost (minimization via MRA on -Cost):\n")
                    for idx_r in sorted_idx:
                        ci = accepted[idx_r]
                        w.insert(tk.END, f"  W={ci['W']:>3} | Cost_total={fmt_iv(ci['cost_total'])} | rank={ranks[idx_r]}\n")
                    chosen = accepted[sorted_idx[0]]  # smallest original cost
                    w.insert(tk.END, f"→ Using Regret, the smaller grey cost is selected: W={chosen['W']} | Cost_total={fmt_iv(chosen['cost_total'])}\n")
                else:
                    # fallback: midpoint of original cost
                    accepted.sort(key=lambda c: 0.5*(c["cost_total"][0] + c["cost_total"][1]))
                    chosen = accepted[0]
                    w.insert(tk.END, "Regret module not available; selected by minimum midpoint of cost.\n")
                    w.insert(tk.END, f"→ Selected (as smaller cost by midpoint): W={chosen['W']} | Cost_total={fmt_iv(chosen['cost_total'])}\n")

                chosen_W = chosen["W"]

            # finalize period
            hire_count = max(0, chosen_W - W_prev)
            fire_count = max(0, W_prev - chosen_W)
            Qreg = chosen["Qreg"]
            cost_pers = chosen["cost_pers"]
            cost_reg  = chosen["cost_reg"]
            cost_hire = chosen["cost_hire"]
            cost_fire = chosen["cost_fire"]
            cost_total = chosen["cost_total"]

            w.insert(tk.END, f"→ Chosen W_t = {chosen_W}{' (forced)' if forced else ''}\n")
            w.insert(tk.END, f"   Hire={hire_count}, Fire={fire_count}, Qreg={fmt_iv(Qreg)}, Total cost={fmt_iv(cost_total)}\n")

            grand_total = grey_add(grand_total, cost_total)
            summary_rows.append((period, D_t, Wreq, chosen_W, hire_count, fire_count,
                                 Qreg, cost_pers, cost_reg, cost_hire, cost_fire, cost_total))
            W_prev = chosen_W

        # ===== Summary =====
        w.insert(tk.END, "\n===== Summary (Chase) =====\n")
        header = ("Period | Demand [a,b] | W_req [a,b] | W | Hire | Fire | "
                  "Qreg [a,b] | Cost_pers | Cost_reg | Cost_hire | Cost_fire | Cost_total")
        w.insert(tk.END, header + "\n")
        w.insert(tk.END, "-"*len(header) + "\n")
        for row in summary_rows:
            period, D_t, Wreq, Wc, H, F, Qreg, cp, cr, ch, cf, ct = row
            w.insert(tk.END,
                     f"{period:>6} | {fmt_iv(D_t):>13} | {fmt_iv(Wreq):>13} | {Wc:>2} | "
                     f"{H:>4} | {F:>4} | {fmt_iv(Qreg):>10} | {fmt_iv(cp):>10} | "
                     f"{fmt_iv(cr):>9} | {fmt_iv(ch):>10} | {fmt_iv(cf):>10} | {fmt_iv(ct):>10}\n")

        w.insert(tk.END, f"\nGrand total cost (Chase): {fmt_iv(grand_total)}\n")
        w.insert(tk.END, "-"*60 + "\n")
        w.insert(tk.END, "Completed.\n")

    # ---------- save/load ----------
    def save_project(self):
        data = {
            "periods": [],
            "params": {
                "W0": self.w0_entry.get().strip(),
                "I0": self.i0_entry.get().strip(),
                "B0": self.b0_entry.get().strip(),
                "P": [self.p_low_entry.get().strip(), self.p_up_entry.get().strip()],
            },
            "costs": {
                "C_reg":  [self.creg_low.get().strip(),  self.creg_up.get().strip()],
                "C_hire": [self.chire_low.get().strip(), self.chire_up.get().strip()],
                "C_fire": [self.cfire_low.get().strip(), self.cfire_up.get().strip()],
                "C_pers": [self.cpers_low.get().strip(), self.cpers_up.get().strip()],
            },
            "result": self.result_widget.get("1.0", tk.END).strip()
        }
        for it in self.tree.get_children():
            period, demand = self.tree.item(it, "values")
            data["periods"].append({"period": period, "demand": demand})

        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Saved", f"Project saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

    def load_project(self):
        path = filedialog.askopenfilename(defaultextension=".json",
                                          filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Load failed: {e}")
            return

        for it in list(self.tree.get_children()):
            self.tree.delete(it)

        for row in data.get("periods", []):
            self.tree.insert("", "end", values=(row.get("period",""), row.get("demand","[ , ]")))

        p = data.get("params", {})
        self.w0_entry.delete(0, tk.END); self.w0_entry.insert(0, p.get("W0",""))
        self.i0_entry.delete(0, tk.END); self.i0_entry.insert(0, p.get("I0",""))
        self.b0_entry.delete(0, tk.END); self.b0_entry.insert(0, p.get("B0",""))
        P = p.get("P", ["",""])
        self.p_low_entry.delete(0, tk.END); self.p_low_entry.insert(0, P[0])
        self.p_up_entry.delete(0,  tk.END); self.p_up_entry.insert(0, P[1])

        c = data.get("costs", {})
        def ins(e, val): e.delete(0, tk.END); e.insert(0, val)
        C_reg  = c.get("C_reg",  ["",""]);  ins(self.creg_low,  C_reg[0]);  ins(self.creg_up,  C_reg[1])
        C_hire = c.get("C_hire", ["",""]);  ins(self.chire_low, C_hire[0]); ins(self.chire_up, C_hire[1])
        C_fire = c.get("C_fire", ["",""]);  ins(self.cfire_low, C_fire[0]); ins(self.cfire_up, C_fire[1])
        C_pers = c.get("C_pers", ["",""]);  ins(self.cpers_low, C_pers[0]); ins(self.cpers_up, C_pers[1])

        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, data.get("result",""))
        messagebox.showinfo("Loaded", f"Project loaded from:\n{path}")
