import tkinter as tk
from main_app import MainApp

class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GST Login")
        self.geometry("500x300")
        self.configure(bg="white")
        tk.Label(self, text="Application of GST in POM", font=("Arial", 20, "bold"), bg="white").pack(pady=5)
        tk.Label(self, text="Contact: tkarimi@ut.ac.ir", font=("Arial", 12), fg="blue", bg="white").pack(pady=5)
        tk.Button(self, text="Login Page", width=20, font=("times new roman", 15), fg="red", bg="yellow",command=self.open_main).pack(pady=60)
        tk.Label(self, text="This app is developed by Tooraj Karimi to facilitate the solving of book examples", font=("Arial", 10), fg="black", bg="white").pack(pady=5)

    def open_main(self):
        self.destroy()
        app = MainApp()
        app.mainloop()

if __name__ == "__main__":
    login = LoginApp()
    login.mainloop()
