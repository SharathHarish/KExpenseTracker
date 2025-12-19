import tkinter as tk
from tkinter import ttk
import sys

CARD_BG = "#1c1c1c"
TEXT_LIGHT = "#ffffff"
FERRARI_RED = "#C4001A"

# Example conversion rate
USD_TO_INR = 91


class SettingsWindow(ttk.Frame):
    def __init__(self, parent, inline=False):
        if not inline:
            self.window = tk.Toplevel(parent)
            self.window.title("Currency Converter")
            self.window.geometry("320x300")
            self.window.configure(bg=CARD_BG)
            parent = self.window

        super().__init__(parent, style="Card.TFrame", padding=15)
        self.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            self,
            text="Conversion",
            style="Card.TLabel",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="center", pady=(0, 15))

        # From Currency
        ttk.Label(self, text="From Currency", style="Card.TLabel").pack(anchor="w")
        self.from_var = tk.StringVar(value="INR")
        ttk.Combobox(
            self,
            values=["INR", "USD"],
            textvariable=self.from_var,
            state="readonly",
        ).pack(fill="x", pady=(2, 8))

        # To Currency
        ttk.Label(self, text="To Currency", style="Card.TLabel").pack(anchor="w")
        self.to_var = tk.StringVar(value="USD")
        ttk.Combobox(
            self,
            values=["INR", "USD"],
            textvariable=self.to_var,
            state="readonly",
        ).pack(fill="x", pady=(2, 8))

        # Amount
        ttk.Label(self, text="Amount", style="Card.TLabel").pack(anchor="w")
        self.amount_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.amount_var).pack(fill="x", pady=(2, 10))

        # Convert Button
        ttk.Button(
            self,
            text="Convert",
            style="Ferrari.TButton",
            command=self.convert,
        ).pack(fill="x", pady=(5, 10))

        # Result
        self.result_label = ttk.Label(
            self,
            text="",
            style="Card.TLabel",
            font=("Segoe UI", 11, "bold"),
        )
        self.result_label.pack(anchor="center", pady=(5, 15))

        # Exit Application Button
        ttk.Button(
            self,
            text="Exit Application",
            style="Ferrari.TButton",
            command=self.exit_app,
        ).pack(fill="x")

    def convert(self):
        try:
            amount = float(self.amount_var.get())
            from_cur = self.from_var.get()
            to_cur = self.to_var.get()

            if from_cur == to_cur:
                result = amount
            elif from_cur == "INR" and to_cur == "USD":
                result = amount / USD_TO_INR
            elif from_cur == "USD" and to_cur == "INR":
                result = amount * USD_TO_INR
            else:
                result = 0

            self.result_label.config(
                text=f"{amount:.2f} {from_cur} = {result:.2f} {to_cur}"
            )

        except ValueError:
            self.result_label.config(text="Enter a valid number")

    def exit_app(self):
        """Exit the entire application"""
        sys.exit(0)
