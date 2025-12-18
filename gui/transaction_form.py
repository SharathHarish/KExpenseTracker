import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from db.repository import Repository
from datetime import datetime

FERRARI_RED = "#C4001A"
BG_DARK = "#0b0b0b"
CARD_BG = "#1c1c1c"
TEXT_LIGHT = "#ffffff"

class TransactionForm(tk.Toplevel):
    def __init__(self, parent, refresh_cb):
        super().__init__(parent)
        self.repo = Repository()
        self.refresh_cb = refresh_cb

        self.title("Add Transaction")
        self.geometry("600x500")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Styles
        self.style.configure("Ferrari.TLabel", background=BG_DARK, foreground=TEXT_LIGHT, font=("Segoe UI", 11))
        self.style.configure("FerrariHeader.TLabel", background=BG_DARK, foreground=FERRARI_RED, font=("Segoe UI", 18, "bold"))
        self.style.configure("Ferrari.TEntry", fieldbackground=CARD_BG, foreground=TEXT_LIGHT, padding=5)
        self.style.configure("Ferrari.TButton", background=FERRARI_RED, foreground="white", font=("Segoe UI", 11, "bold"), padding=8)
        self.style.map("Ferrari.TButton", background=[("active", "#e1062c")])
        self.style.configure("Ferrari.TCombobox", fieldbackground=CARD_BG, foreground=TEXT_LIGHT, background=CARD_BG)

        # Container Card
        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        card['borderwidth'] = 2
        card['relief'] = 'ridge'

        ttk.Label(card, text="Add New Transaction", style="FerrariHeader.TLabel").grid(row=0, column=0, columnspan=2, pady=(0,20))

        self.entries = {}
        fields = [
            ("Date", "date", "date"),
            ("Amount", "amount", "entry"),
            ("Type", "type", ["Income", "Expense"]),
            ("Category", "category", []),
            ("Payment Method", "payment", ["Cash", "Card", "UPI", "Wallet"]),
            ("Tags", "tags", "entry")
        ]

        for i, (label_text, key, field_type) in enumerate(fields):
            row = 1 + i // 2
            col = i % 2

            ttk.Label(card, text=label_text, style="Ferrari.TLabel").grid(row=row*2-1, column=col, sticky="w", padx=5, pady=(5,2))

            if field_type == "date":
                entry = DateEntry(card, background=FERRARI_RED, foreground="white", borderwidth=2, date_pattern='yyyy-mm-dd')
                entry.set_date(datetime.now())
            elif field_type == "entry":
                entry = ttk.Entry(card, style="Ferrari.TEntry")
            elif isinstance(field_type, list):
                entry = ttk.Combobox(card, values=field_type, style="Ferrari.TCombobox", state="readonly")
                if key == "type":
                    entry.set("Income")  # default type
            entry.grid(row=row*2, column=col, sticky="ew", padx=5, pady=(0,10))
            self.entries[key] = entry

        # Bind Type selection to dynamically update Category
        self.entries["type"].bind("<<ComboboxSelected>>", self.update_category_options)
        self.update_category_options()  # set initial categories for default type

        # Make columns expand equally
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        # SAVE button at bottom spanning both columns
        save_btn = ttk.Button(card, text="SAVE", style="Ferrari.TButton", command=self.save)
        save_btn.grid(row=(len(fields)//2 + 2)*2, column=0, columnspan=2, sticky="ew", pady=20)

    def update_category_options(self, event=None):
        type_selected = self.entries["type"].get()
        if type_selected.lower() == "income":
            categories = ["Salary", "Trading", "Other"]
        else:
            categories = ["Food", "Transport", "Cloth", "Loan", "Other"]

        self.entries["category"]["values"] = categories
        self.entries["category"].set('')  # clear previous selection

    def save(self):
        # Validate all fields
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"Please fill the '{key.capitalize()}' field.")
                return  # don't close form

        try:
            data = (
                self.entries["date"].get(),
                float(self.entries["amount"].get()),
                self.entries["type"].get().lower(),
                self.entries["category"].get(),
                self.entries["payment"].get(),
                self.entries["tags"].get()
            )
            self.repo.add_transaction(data)
            self.refresh_cb()
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
