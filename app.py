import tkinter as tk
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("Personal Expense Tracker")
    root.geometry("1000x1020")
    MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
