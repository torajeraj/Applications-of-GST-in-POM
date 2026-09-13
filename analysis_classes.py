import tkinter as tk
from tkinter import messagebox, filedialog as fd
import pandas as pd

class AnalysisBase:
    def __init__(self, input_frame, result_text):
        self.input_frame = input_frame
        self.result_text = result_text
        self.seq_data = []

    def load_excel(self):
        file_path = fd.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return
        try:
            df = pd.read_excel(file_path, header=None)
            self.seq_data = df.values.tolist()
            display_text = "Loaded sequences from Excel:\n"
            for i, row in enumerate(self.seq_data, 1):
                display_text += f"X{i}: {', '.join(str(x) for x in row)}\n"
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading Excel file: {e}")

class DengAnalysis(AnalysisBase):
    def show_inputs(self):
        for w in self.input_frame.winfo_children():
            w.destroy()
        tk.Label(self.input_frame, text="Sequence 1 (comma separated):").pack(fill="x")
        self.entry1 = tk.Entry(self.input_frame, width=60)
        self.entry1.pack(fill="x", pady=2)
        tk.Label(self.input_frame, text="Sequence 2 (comma separated):").pack(fill="x")
        self.entry2 = tk.Entry(self.input_frame, width=60)
        self.entry2.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Import Excel File", command=self.load_excel).pack(pady=10)
        tk.Label(self.input_frame, text="Precision (decimal digits):").pack(fill="x")
        self.precision_entry = tk.Entry(self.input_frame, width=10)
        self.precision_entry.pack(fill="x", pady=2)
        tk.Label(self.input_frame, text="Distinguishing coefficient (Deng):").pack(fill="x")
        self.coeff_entry = tk.Entry(self.input_frame, width=10)
        self.coeff_entry.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Calculate", command=self.calculate).pack(pady=10)
    def calculate(self):
        from grey_incidence import DengIncidence
        try:
            precision = int(self.precision_entry.get())
            coef = float(self.coeff_entry.get())
        except:
            messagebox.showerror("Input Error", "Invalid precision or coefficient.")
            return
        deng = DengIncidence()
        if self.seq_data:
            sequences = self.seq_data
        else:
            try:
                seq1 = [float(x.strip()) for x in self.entry1.get().split(",") if x.strip()]
                seq2 = [float(x.strip()) for x in self.entry2.get().split(",") if x.strip()]
                sequences = [seq1, seq2]
            except:
                messagebox.showerror("Input Error", "Invalid manual sequences.")
                return
        if len(sequences) < 2:
            messagebox.showwarning("Input Error", "At least two sequences required.")
            return
        output = ""
        n = len(sequences)
        for i in range(n):
            for j in range(i+1, n):
                steps_text, degrees = deng.compute_all_steps(sequences[i], sequences[j], coef, precision)
                output += steps_text
                output += f"Step 6: Deng's Degree of Incidence X{i+1}, X{j+1} = {', '.join(f'{deg:.{precision}f}' for deg in degrees)}\n\n"
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, output)

# مشابه برای کلاس های دیگر:

class AbsoluteAnalysis(AnalysisBase):
    def show_inputs(self):
        for w in self.input_frame.winfo_children():
            w.destroy()
        tk.Label(self.input_frame, text="Sequence 1 (comma separated):").pack(fill="x")
        self.entry1 = tk.Entry(self.input_frame, width=60)
        self.entry1.pack(fill="x", pady=2)
        tk.Label(self.input_frame, text="Sequence 2 (comma separated):").pack(fill="x")
        self.entry2 = tk.Entry(self.input_frame, width=60)
        self.entry2.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Import Excel File", command=self.load_excel).pack(pady=10)
        tk.Label(self.input_frame, text="Precision (decimal digits):").pack(fill="x")
        self.precision_entry = tk.Entry(self.input_frame, width=10)
        self.precision_entry.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Calculate", command=self.calculate).pack(pady=10)
    def calculate(self):
        try:
            precision = int(self.precision_entry.get())
        except:
            messagebox.showerror("Input Error", "Invalid precision.")
            return
        from grey_incidence import AbsoluteIncidence
        abs_inc = AbsoluteIncidence(None, precision)
        if self.seq_data:
            data = self.seq_data
        else:
            try:
                seq1 = [float(x.strip()) for x in self.entry1.get().split(",") if x.strip()]
                seq2 = [float(x.strip()) for x in self.entry2.get().split(",") if x.strip()]
                data = [seq1, seq2]
            except:
                messagebox.showerror("Input Error", "Invalid manual sequences.")
                return
        if len(data) < 2:
            messagebox.showwarning("Input Error", "At least two sequences required.")
            return
        abs_inc.data = data
        result = abs_inc.calculate()
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)

class RelativeAnalysis(AnalysisBase):
    def show_inputs(self):
        for w in self.input_frame.winfo_children():
            w.destroy()
        tk.Label(self.input_frame, text="Sequence 1 (comma separated):").pack(fill="x")
        self.entry1 = tk.Entry(self.input_frame, width=60)
        self.entry1.pack(fill="x", pady=2)
        tk.Label(self.input_frame, text="Sequence 2 (comma separated):").pack(fill="x")
        self.entry2 = tk.Entry(self.input_frame, width=60)
        self.entry2.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Import Excel File", command=self.load_excel).pack(pady=10)
        tk.Label(self.input_frame, text="Precision (decimal digits):").pack(fill="x")
        self.precision_entry = tk.Entry(self.input_frame, width=10)
        self.precision_entry.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Calculate", command=self.calculate).pack(pady=10)
    def calculate(self):
        try:
            precision = int(self.precision_entry.get())
        except:
            messagebox.showerror("Input Error", "Invalid precision.")
            return
        from grey_incidence import RelativeIncidence, AbsoluteIncidence
        rel_inc = RelativeIncidence()
        if self.seq_data:
            data = self.seq_data
        else:
            try:
                seq1 = [float(x.strip()) for x in self.entry1.get().split(",") if x.strip()]
                seq2 = [float(x.strip()) for x in self.entry2.get().split(",") if x.strip()]
                data = [seq1, seq2]
            except:
                messagebox.showerror("Input Error", "Invalid manual sequences.")
                return
        if len(data) < 2:
            messagebox.showwarning("Input Error", "At least two sequences required.")
            return
        data = rel_inc.getInitialValueImage(data)
        abs_inc = AbsoluteIncidence(data, precision)
        result = abs_inc.calculate()
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)

class SynthesisAnalysis(AnalysisBase):
    def show_inputs(self):
        for w in self.input_frame.winfo_children():
            w.destroy()
        tk.Label(self.input_frame, text="Sequence 1 (comma separated):").pack(fill="x")
        self.entry1 = tk.Entry(self.input_frame, width=60)
        self.entry1.pack(fill="x", pady=2)
        tk.Label(self.input_frame, text="Sequence 2 (comma separated):").pack(fill="x")
        self.entry2 = tk.Entry(self.input_frame, width=60)
        self.entry2.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Import Excel File", command=self.load_excel).pack(pady=10)
        tk.Label(self.input_frame, text="Precision (decimal digits):").pack(fill="x")
        self.precision_entry = tk.Entry(self.input_frame, width=10)
        self.precision_entry.pack(fill="x", pady=2)
        tk.Label(self.input_frame, text="Weight (Synthesis):").pack(fill="x")
        self.weight_entry = tk.Entry(self.input_frame, width=10)
        self.weight_entry.pack(fill="x", pady=2)
        tk.Button(self.input_frame, text="Calculate", command=self.calculate).pack(pady=10)
    def calculate(self):
        try:
            precision = int(self.precision_entry.get())
            weight = float(self.weight_entry.get())
        except:
            messagebox.showerror("Input Error", "Invalid precision or weight.")
            return
        from grey_incidence import SynthesisIncidence
        if self.seq_data:
            data = self.seq_data
        else:
            try:
                seq1 = [float(x.strip()) for x in self.entry1.get().split(",") if x.strip()]
                seq2 = [float(x.strip()) for x in self.entry2.get().split(",") if x.strip()]
                data = [seq1, seq2]
            except:
                messagebox.showerror("Input Error", "Invalid manual sequences.")
                return
        if len(data) < 2:
            messagebox.showwarning("Input Error", "At least two sequences required.")
            return
        synth_inc = SynthesisIncidence(data, precision, weight)
        result = synth_inc.calculate()
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)
