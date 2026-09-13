import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
import pandas as pd

class GM11Input(tk.Frame):
    def __init__(self, parent, result_widget):
        super().__init__(parent)
        self.result_widget = result_widget

        tk.Label(self, text="Enter data sequence (comma separated) or select Excel file with multiple rows:").pack(pady=5)
        self.data_entry = tk.Entry(self, width=60)
        self.data_entry.pack(pady=5)

        tk.Button(self, text="Load from Excel", command=self.load_excel).pack(pady=5)

        precision_frame = tk.Frame(self)
        tk.Label(precision_frame, text="Precision (decimal digits):").pack(side="left", padx=5)
        self.precision_entry = tk.Entry(precision_frame, width=5)
        self.precision_entry.insert(0, "4")
        self.precision_entry.pack(side="left", padx=5)

        tk.Label(precision_frame, text="Forecasted periods:").pack(side="left", padx=5)
        self.forecast_entry = tk.Entry(precision_frame, width=5)
        self.forecast_entry.insert(0, "3")
        self.forecast_entry.pack(side="left", padx=5)
        precision_frame.pack(pady=5)

        tk.Button(self, text="Calculate GM(1,1)", command=self.calculate).pack(pady=10)

    def load_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            try:
                df = pd.read_excel(path, header=None)
                self.excel_data = df.dropna(how='all')  # کل دیتا
                self.data_entry.delete(0, tk.END)
                self.data_entry.insert(0, f"Loaded {len(self.excel_data)} row(s) from Excel")
            except Exception as e:
                messagebox.showerror("File Error", str(e))

    def calculate(self):
        precision = 4
        forecast_len = 3
        try:
            precision = int(self.precision_entry.get())
        except:
            messagebox.showerror("Input Error", "Invalid precision")
            return
        try:
            forecast_len = int(self.forecast_entry.get())
            if forecast_len < 1:
                messagebox.showwarning("Input Error", "Number of forecasted periods must be positive")
                return
        except:
            messagebox.showerror("Input Error", "Invalid number of forecasted periods")
            return

        if hasattr(self, 'excel_data') and len(self.excel_data) > 0:
            # فراخوانی برای چند سطر Excel
            all_results = []
            for idx, row in self.excel_data.iterrows():
                try:
                    data_list = [float(x) for x in row.dropna()]
                    res_text = self.process_gm11(data_list, precision, forecast_len)
                    all_results.append(f"Row {idx+1} results:\n{res_text}")
                except Exception as e:
                    all_results.append(f"Row {idx+1} error: {str(e)}")
            final_output = "\n\n-----------------------------------\n\n".join(all_results)
            self.result_widget.delete(1.0, tk.END)
            self.result_widget.insert(tk.END, final_output)
        else:
            # داده از ورودی متنی گرفته شود
            raw_data = self.data_entry.get()
            try:
                data_list = [float(x.strip()) for x in raw_data.split(",") if x.strip()]
                if len(data_list) < 4:
                    messagebox.showwarning("Input Error", "Input sequence should have at least 4 numbers")
                    return
            except:
                messagebox.showerror("Input Error", "Invalid input sequence")
                return
            res_text = self.process_gm11(data_list, precision, forecast_len)
            self.result_widget.delete(1.0, tk.END)
            self.result_widget.insert(tk.END, res_text)

    def process_gm11(self, data_list, precision, forecast_len):
        x0 = np.array(data_list)
        n = len(x0)
        x1 = np.cumsum(x0)

        z1 = np.array([0.5*(x1[i]+x1[i-1]) for i in range(1, n)])
        B = np.vstack((-z1, np.ones(n-1))).T
        Y = x0[1:].reshape(n-1, 1)

        [[a], [b]] = np.linalg.inv(B.T @ B) @ B.T @ Y

        def hat_x1(k):
            return (x0[0] - b/a) * np.exp(-a * (k - 1)) + b/a

        full_len = n + forecast_len
        hat_x1_values = [hat_x1(k) for k in range(1, full_len + 1)]

        hat_x0_values = [hat_x1_values[0]] + [hat_x1_values[i] - hat_x1_values[i-1] for i in range(1, full_len)]

        residuals = x0 - np.array(hat_x0_values[:n])
        relative_errors = np.abs(residuals / x0)
        avg_relative_error = np.mean(relative_errors) * 100

        model_str = f"x(k) = ({x0[0]:.{precision}f} - {b / a:.{precision}f}) / {a:.{precision}f} * e^(-{a:.{precision}f}(k-1)) + {b / a:.{precision}f}"

        output_lines = [
            f"Raw sequence: {', '.join(f'{v:.{precision}f}' for v in x0)}",
            f"Accumulated generation (1-AGO): {', '.join(f'{v:.{precision}f}' for v in x1)}",
            f"Parameter a: {a:.{precision}f}",
            f"Parameter b: {b:.{precision}f}",
            "Model formula:",
            model_str,
            f"Simulated values: {', '.join(f'{v:.{precision}f}' for v in hat_x0_values[:n])}",
            f"Residual errors: {', '.join(f'{v:.{precision}f}' for v in residuals)}",
            f"Relative errors (%): {', '.join(f'{v*100:.{precision}f}%' for v in relative_errors)}",
            f"Average relative error (%): {avg_relative_error:.{precision}f}",
            f"Forecasted next {forecast_len} periods: {', '.join(f'{v:.{precision}f}' for v in hat_x0_values[n:])}"
        ]
        return "\n\n".join(output_lines)
