import tkinter as tk
from tkinter import ttk, messagebox
from db.repository import Repository
from datetime import datetime

CARD_BG = "#1c1c1c"
TEXT_LIGHT = "#ffffff"
FERRARI_RED = "#C4001A"


class TransactionList(ttk.Treeview):
    def __init__(self, parent, refresh_reports_cb=None):
        self.container = parent
        self.repo = Repository()
        self.refresh_reports_cb = refresh_reports_cb
        self.row_buttons = {}

        # ================= FILTER BAR =================
        filter_frame = tk.Frame(parent, bg=CARD_BG)
        filter_frame.pack(fill="x", pady=(0, 8))

        # ---------- MONTH ----------
        tk.Label(filter_frame, text="Month", bg=CARD_BG, fg=TEXT_LIGHT).pack(
            side="left", padx=(10, 5)
        )

        self.month_var = tk.StringVar(value="All")
        self.month_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.month_var,
            state="readonly",
            width=12,
            values=[
                "All", "January", "February", "March", "April",
                "May", "June", "July", "August",
                "September", "October", "November", "December",
            ],
        )
        self.month_cb.pack(side="left", padx=5)
        self.month_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # ---------- YEAR ----------
        tk.Label(filter_frame, text="Year", bg=CARD_BG, fg=TEXT_LIGHT).pack(
            side="left", padx=(20, 5)
        )

        self.year_var = tk.StringVar()
        self.year_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.year_var,
            state="readonly",
            width=8,
        )
        self.year_cb.pack(side="left", padx=5)
        self.year_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # ================= TABLE =================
        columns = (
            "Date",
            "Amount",
            "Type",
            "Category",
            "Payment Method",
            "Tags",
            "Actions",
        )
        super().__init__(parent, columns=columns, show="headings")
        self.pack(fill="both", expand=True)

        # ================= STYLE =================
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=CARD_BG,
            foreground=TEXT_LIGHT,
            fieldbackground=CARD_BG,
            rowheight=28,
            font=("Segoe UI", 11),
            padding=(4, 4, 4, 4),  # Reduced padding for tighter layout
        )
        style.map(
            "Treeview",
            background=[("selected", FERRARI_RED)],
            foreground=[("selected", "white")],
        )
        style.configure(
            "Treeview.Heading",
            background=FERRARI_RED,
            foreground="white",
            font=("Segoe UI", 11, "bold"),
        )

        # Reduce column width for tighter layout
        for col in columns:
            self.heading(col, text=col)
            self.column(col, anchor="center", width=100, stretch=False)

        # Populate years + set default
        self._populate_years()

        self.refresh()

    # ======================================================
    # POPULATE YEAR DROPDOWN (DEFAULT = CURRENT YEAR)
    # ======================================================
    def _populate_years(self):
        years = set()
        for row in self.repo.fetch_transactions():
            year = datetime.strptime(row[1], "%Y-%m-%d").year
            years.add(str(year))

        current_year = str(datetime.now().year)
        year_list = ["All"] + sorted(years, reverse=True)
        self.year_cb["values"] = year_list

        # ✅ Default year = current year (if exists)
        if current_year in year_list:
            self.year_var.set(current_year)
        else:
            self.year_var.set("All")

    # ======================================================
    # REFRESH TABLE + REPORTS
    # ======================================================
    def refresh(self):
        self.delete(*self.get_children())
        for btn in self.row_buttons.values():
            btn.destroy()
        self.row_buttons.clear()

        month = self.month_var.get()
        year = self.year_var.get()

        for row in self.repo.fetch_transactions():
            txn_id = row[0]
            txn_date = datetime.strptime(row[1], "%Y-%m-%d")

            if month != "All" and txn_date.strftime("%B") != month:
                continue
            if year != "All" and str(txn_date.year) != year:
                continue

            self.insert("", "end", iid=txn_id, values=row[1:8])
            self._add_remove_button(txn_id)

        # 🔥 Sync reports
        if self.refresh_reports_cb:
            self.refresh_reports_cb()

    # ======================================================
    # REMOVE BUTTON
    # ======================================================
    def _add_remove_button(self, txn_id):
        bbox = self.bbox(txn_id, column=6)
        if not bbox:
            self.after(100, lambda: self._add_remove_button(txn_id))
            return

        x, y, w, h = bbox
        btn = tk.Button(
            self.container,
            text="Remove",
            bg=FERRARI_RED,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=lambda tid=txn_id: self.delete_transaction(tid),
        )
        btn.place(
            x=x + self.winfo_x(),
            y=y + self.winfo_y(),
            width=w,
            height=h,
        )
        self.row_buttons[txn_id] = btn

    # ======================================================
    # DELETE TRANSACTION
    # ======================================================
    def delete_transaction(self, txn_id):
        if not messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this transaction?"
        ):
            return

        try:
            self.repo.delete_transaction(txn_id)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))
