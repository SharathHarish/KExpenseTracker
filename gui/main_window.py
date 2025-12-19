import tkinter as tk
from tkinter import ttk
from gui.transaction_form import TransactionForm
from gui.transaction_list import TransactionList
from gui.reports import ReportsWindow
from gui.settings import SettingsWindow
from db.models import init_db

# Ferrari theme colors
FERRARI_RED = "#C4001A"
BG_DARK = "#0b0b0b"
CARD_BG = "#1c1c1c"
TEXT_LIGHT = "#ffffff"


class MainWindow:
    def __init__(self, root):
        init_db()
        self.root = root
        self.root.title("K Personal Expense Checker")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1200x700")

        self.setup_style()
        self.build_header()
        self.build_dashboard()

    # ---------------- STYLES ----------------
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Ferrari.TButton",
            background=FERRARI_RED,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=10,
        )
        style.map("Ferrari.TButton", background=[("active", "#e1062c")])

        style.configure("Card.TFrame", background=CARD_BG)

        style.configure(
            "Card.TLabel",
            background=CARD_BG,
            foreground=TEXT_LIGHT,
            font=("Segoe UI", 11),
        )

        style.configure(
            "Title.TLabel",
            background=BG_DARK,
            foreground=FERRARI_RED,
            font=("Segoe UI", 22, "bold"),
        )

    # ---------------- HEADER ----------------
    def build_header(self):
        header = ttk.Frame(self.root, style="Card.TFrame")
        header.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            header,
            text="K PERSONAL EXPENSE CHECKER",
            style="Title.TLabel",
        ).pack(side="left", padx=10)

        ttk.Button(
            header,
            text="+ ADD TRANSACTION",
            style="Ferrari.TButton",
            command=self.open_add,
        ).pack(side="right", padx=10)

    # ---------------- DASHBOARD ----------------
    def build_dashboard(self):
        content = ttk.Frame(self.root, style="Card.TFrame")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Configure grid: 3 columns
        content.columnconfigure(0, weight=5)  # Left - Transactions
        content.columnconfigure(1, weight=3)  # Middle - Reports
        content.columnconfigure(2, weight=2)  # Right - Settings

        content.rowconfigure(0, weight=1)

        # -------- LEFT : TRANSACTIONS --------
        left = ttk.Frame(content, style="Card.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(left, text="Recent Transactions", style="Card.TLabel") \
            .pack(anchor="w", padx=10, pady=5)

        self.list_view = TransactionList(
            left,
            refresh_reports_cb=self.refresh_reports
        )
        self.list_view.pack(fill="both", expand=True, padx=10, pady=10)

        # -------- MIDDLE : REPORTS --------
        middle = ttk.Frame(content, style="Card.TFrame")
        middle.grid(row=0, column=1, sticky="nsew", padx=(0, 10))

        ttk.Label(middle, text="Reports", style="Card.TLabel") \
            .pack(anchor="w", padx=10, pady=5)

        self.reports_view = ReportsWindow(middle, inline=True)
        self.reports_view.pack(fill="both", expand=True, padx=10, pady=10)

        # -------- RIGHT : SETTINGS --------
        right = ttk.Frame(content, style="Card.TFrame")
        right.grid(row=0, column=2, sticky="nsew")

        ttk.Label(right, text="Settings", style="Card.TLabel") \
            .pack(anchor="w", padx=10, pady=5)

        self.settings_view = SettingsWindow(right, inline=True)
        self.settings_view.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- GLOBAL REFRESH ----------------
    def refresh_all(self):
        """Refresh list + reports together"""
        self.list_view.refresh()
        self.refresh_reports()

    def refresh_reports(self):
        if hasattr(self, "reports_view"):
            self.reports_view.refresh()

    # ---------------- ADD TRANSACTION ----------------
    def open_add(self):
        TransactionForm(self.root, self.refresh_all)
