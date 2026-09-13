import tkinter as tk
from tkinter import messagebox


# -------------------------------
# عملیات روی اعداد خاکستری
# -------------------------------
def grey_add(a, b):
    """جمع خاکستری [a1,a2] + [b1,b2]"""
    return (a[0] + b[0], a[1] + b[1])


def grey_subtract(a, b):
    """تفریق خاکستری [a1,a2] - [b1,b2]"""
    return (a[0] - b[1], a[1] - b[0])


def grey_multiply(a, b):
    """ضرب خاکستری [a1,a2] × [b1,b2]"""
    values = [
        a[0] * b[0], a[0] * b[1],
        a[1] * b[0], a[1] * b[1]
    ]
    return (min(values), max(values))


def grey_divide(a, b):
    """
    تقسیم خاکستری [a1,a2] ÷ [b1,b2]
    [min(a/c,a/d,b/c,b/d), max(...)]
    به شرطی که [c,d] شامل صفر نباشه.
    """
    low_a, up_a = a
    low_b, up_b = b

    if low_b <= 0 <= up_b:
        raise ZeroDivisionError("Division by interval containing zero is not allowed.")

    values = [
        low_a / low_b, low_a / up_b,
        up_a / low_b, up_a / up_b
    ]
    return (min(values), max(values))


def grey_power(a, k):
    """توان خاکستری [a1,a2]^k (k ≥ 0)"""
    if k < 0:
        raise ValueError("Exponent must be non-negative.")
    return (a[0] ** k, a[1] ** k)


# -------------------------------
# کلاس UI برای محاسبات خاکستری
# -------------------------------
class GreyNumberOperationInput(tk.Frame):
    operators = ["+", "-", "×", "÷", "^"]

    def __init__(self, parent, result_widget):
        super().__init__(parent)
        self.result_widget = result_widget
        self.max_numbers = 6
        self.entries = []
        self.op_vars = []

        tk.Label(
            self,
            text="Enter grey numbers and select operations:\n(for crisp number enter lower=upper)",
            bg="#2a2a2a", fg="white"
        ).grid(row=0, column=0, columnspan=5, pady=5)

        for i in range(self.max_numbers):
            tk.Label(self, text=f"X{i+1} Lower:", bg="#2a2a2a", fg="white").grid(row=1+i, column=0, sticky="w")
            tk.Label(self, text=f"X{i+1} Upper:", bg="#2a2a2a", fg="white").grid(row=1+i, column=2, sticky="w")

            low_var, up_var, op_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
            op_var.set("")

            low_entry = tk.Entry(self, textvariable=low_var, width=12)
            up_entry = tk.Entry(self, textvariable=up_var, width=12)
            op_menu = tk.OptionMenu(self, op_var, *self.operators,
                                    command=lambda e, idx=i: self.operator_selected(idx))

            low_entry.grid(row=1+i, column=1, padx=5, pady=2)
            up_entry.grid(row=1+i, column=3, padx=5, pady=2)
            op_menu.grid(row=1+i, column=4, padx=5)

            self.entries.append((low_var, up_var))
            self.op_vars.append(op_var)

        self.calc_btn = tk.Button(self, text="Compute Operations", command=self.compute_operations)
        self.calc_btn.grid(row=self.max_numbers+2, column=0, columnspan=5, pady=10)

        self.displayed_results = ""

    def operator_selected(self, index):
        if index == self.max_numbers - 1:
            return
        next_low_var, next_up_var = self.entries[index + 1]
        try:
            float(next_low_var.get()); float(next_up_var.get())
        except ValueError:
            messagebox.showwarning("Warning", f"Enter numbers for X{index+2} before selecting operator.")
            self.op_vars[index].set("")

    def compute_operations(self):
        grey_numbers = []
        for i, (low_var, up_var) in enumerate(self.entries):
            low_s, up_s = low_var.get().strip(), up_var.get().strip()
            if not low_s or not up_s:
                continue
            try:
                low_val, up_val = float(low_s), float(up_s)
                if low_val > up_val:
                    messagebox.showerror("Error", f"Lower must be ≤ Upper for X{i+1}")
                    return
                grey_numbers.append((low_val, up_val))
            except ValueError:
                messagebox.showerror("Error", f"Invalid input for X{i+1}")
                return

        if len(grey_numbers) < 2:
            messagebox.showwarning("Warning", "Enter at least two grey numbers.")
            return

        operators = []
        for i in range(len(grey_numbers)-1):
            op = self.op_vars[i].get()
            if op not in self.operators:
                messagebox.showerror("Error", f"Operator missing at row {i+1}")
                return
            operators.append(op)

        current_num = grey_numbers[0]
        self.displayed_results = ""
        for i, op in enumerate(operators):
            next_num = grey_numbers[i+1]
            result = self.calculate_operation(current_num, next_num, op)
            self.displayed_results += f"Step {i+1}: {current_num} {op} {next_num} = {result}\n"
            current_num = result

        # نمایش در ویجت قابل کپی
        self.result_widget.delete("1.0", tk.END)
        self.result_widget.insert(tk.END, self.displayed_results)

    def calculate_operation(self, a, b, op):
        if op == "+": return grey_add(a, b)
        if op == "-": return grey_subtract(a, b)
        if op == "×": return grey_multiply(a, b)
        if op == "÷": return grey_divide(a, b)
        if op == "^": return grey_power(a, int(b[0]))
        raise ValueError(f"Unknown operator {op}")


# -------------------------------
# تست مستقیم
# -------------------------------
if __name__ == "__main__":
    X = (-6, 3)
    Y = (4, 8)
    print("X+Y =", grey_add(X, Y))       # (-2, 11)
    print("X-Y =", grey_subtract(X, Y)) # (-14, -1)
    print("X*Y =", grey_multiply(X, Y)) # (-48, 24)
    print("X/Y =", grey_divide(X, Y))   # (-1.5, 0.75)
