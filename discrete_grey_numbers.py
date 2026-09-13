# discrete_grey_numbers.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

from grey_comparison import DiscreteGreyNumberComparator


class DiscreteGreyNumberInput(tk.Frame):
    """
    UI for 'Discrete grey numbers' comparison.
    One table, each row = one discrete grey number set.
      - Values: comma-separated floats (duplicates allowed)
      - Probabilities: comma-separated floats (optional).
        * If empty, probabilities are inferred from relative frequencies of DISTINCT values.
        * If provided, length must match the number of values; duplicates will be aggregated and normalized.
    Supports comparing TWO OR MORE sets:
      - Builds pairwise matrices P(>), P(=), and Advantage M_adv = P(>) + 0.5 P(=)
      - Ranks sets by sum of row M_adv (largest -> smallest)
    """
    def __init__(self, parent, result_widget):
        super().__init__(parent, bg="#2a2a2a")
        self.result_widget = result_widget
        self.selected_item = None

        # ===== Table =====
        self.tree = ttk.Treeview(self, columns=("set","values","probs"), show="headings", height=8)
        self.tree.heading("set", text="Set")
        self.tree.heading("values", text="Values (comma-separated)")
        self.tree.heading("probs", text="Probabilities (comma-separated, optional)")
        self.tree.column("set", width=100, anchor="center")
        self.tree.column("values", width=420, anchor="w")
        self.tree.column("probs", width=420, anchor="w")
        self.tree.pack(fill="x", pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ===== Form =====
        form = tk.Frame(self, bg="#2a2a2a"); form.pack(fill="x", pady=6)
        tk.Label(form, text="Set label:", bg="#2a2a2a", fg="white").grid(row=0, column=0, sticky="w")
        self.set_entry = tk.Entry(form, width=12); self.set_entry.grid(row=0, column=1, padx=4)

        tk.Label(form, text="Values (e.g., 100,200,100,0,200):", bg="#2a2a2a", fg="white").grid(row=0, column=2, sticky="w")
        self.values_entry = tk.Entry(form, width=55); self.values_entry.grid(row=0, column=3, padx=4)

        tk.Label(form, text="Probabilities (optional, same length):", bg="#2a2a2a", fg="white").grid(row=0, column=4, sticky="w")
        self.probs_entry = tk.Entry(form, width=55); self.probs_entry.grid(row=0, column=5, padx=4)

        # ===== Row buttons =====
        rows = tk.Frame(self, bg="#2a2a2a"); rows.pack(fill="x", pady=4)
        self.add_btn = tk.Button(rows, text="Add row", command=self.add_row); self.add_btn.pack(side="left", padx=5)
        self.update_btn = tk.Button(rows, text="Update row", state="disabled", command=self.update_row); self.update_btn.pack(side="left", padx=5)
        tk.Button(rows, text="Clear form", command=self.clear_form).pack(side="left", padx=5)

        # ===== Footer =====
        foot = tk.Frame(self, bg="#2a2a2a"); foot.pack(fill="x", pady=8)
        tk.Button(foot, text="Save Project", command=self.save_project).pack(side="left", padx=5)
        tk.Button(foot, text="Load Project", command=self.load_project).pack(side="left", padx=5)
        tk.Button(foot, text="Preview", command=self.preview).pack(side="left", padx=5)
        tk.Button(foot, text="Run", command=self.run).pack(side="left", padx=5)

    # ---------- helpers ----------
    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel: return
        self.selected_item = sel[0]
        s, v, p = self.tree.item(self.selected_item, "values")
        self.set_entry.delete(0, tk.END); self.set_entry.insert(0, s)
        self.values_entry.delete(0, tk.END); self.values_entry.insert(0, v)
        self.probs_entry.delete(0, tk.END); self.probs_entry.insert(0, p)
        self.update_btn.config(state="normal")
        self.add_btn.config(state="disabled")

    def clear_form(self):
        """Clear inputs + fully clear table selection + reset buttons."""
        self.set_entry.delete(0, tk.END)
        self.values_entry.delete(0, tk.END)
        self.probs_entry.delete(0, tk.END)
        try:
            self.tree.selection_set(())
            self.tree.focus("")
        except Exception:
            try:
                for sel in self.tree.selection():
                    self.tree.selection_remove(sel)
            except Exception:
                pass
        self.selected_item = None
        self.update_btn.config(state="disabled")
        self.add_btn.config(state="normal")

    # ---------- rows CRUD ----------
    def add_row(self):
        s = (self.set_entry.get().strip() or f"Set{len(self.tree.get_children())+1}")
        v = self.values_entry.get().strip()
        if not v:
            messagebox.showerror("Input error", "Values cannot be empty.")
            return
        p = self.probs_entry.get().strip()
        self.tree.insert("", "end", values=(s, v, p))
        self.clear_form()

    def update_row(self):
        if not self.selected_item: return
        s = (self.set_entry.get().strip() or "Set")
        v = self.values_entry.get().strip()
        if not v:
            messagebox.showerror("Input error", "Values cannot be empty.")
            return
        p = self.probs_entry.get().strip()
        self.tree.item(self.selected_item, values=(s, v, p))
        self.clear_form()

    # ---------- save/load ----------
    def save_project(self):
        data = {"sets":[]}
        for ch in self.tree.get_children():
            s, v, p = self.tree.item(ch, "values")
            data["sets"].append({"set": s, "values": v, "probs": p})
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")], title="Save Discrete Grey Project")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Saved", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def load_project(self):
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON","*.json")], title="Load Discrete Grey Project")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load:\n{e}"); return
        for ch in self.tree.get_children():
            self.tree.delete(ch)
        for row in data.get("sets", []):
            self.tree.insert("", "end", values=(row.get("set",""), row.get("values",""), row.get("probs","")))
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "Project loaded. Use Preview or Run.\n")

    # ---------- preview & run ----------
    def preview(self):
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "Discrete grey numbers — Input preview\n\n")
        if len(self.tree.get_children()) == 0:
            self.result_widget.insert(tk.END, "  (no rows)\n"); return
        for ch in self.tree.get_children():
            s, v, p = self.tree.item(ch, "values")
            p_show = p if p.strip() else "(auto from multiplicity)"
            self.result_widget.insert(tk.END, f"  - {s}: values=[{v}], p={p_show}\n")

    def run(self):
        rows = self.tree.get_children()
        if len(rows) < 2:
            messagebox.showwarning("Need ≥2 sets", "Please enter at least two rows (sets) to compare.")
            return

        # Collect all sets
        items = []
        for r in rows:
            s, v, p = self.tree.item(r, "values")
            if not (v and v.strip()):
                messagebox.showerror("Input error", f"Values cannot be empty (row label: {s}).")
                return
            items.append((s, v.strip(), p.strip()))

        try:
            labels, M_gt, M_eq, M_adv, scores, order, log = DiscreteGreyNumberComparator.compare_many(items)
        except Exception as e:
            messagebox.showerror("Run Error", str(e))
            return

        # Print: matrices + ranking
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, "Multi-set discrete grey comparison\n\n")
        self.result_widget.insert(tk.END, log + "\n")
