import tkinter as tk
from tkinter import ttk, messagebox
from db.repository import Repository

CARD_BG = "#1c1c1c"
TEXT_LIGHT = "#ffffff"
FERRARI_RED = "#C4001A"


class TransactionList(ttk.Treeview):
    def __init__(self, parent, refresh_reports_cb=None):
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

        self.repo = Repository()
        self.parent = parent
        self.refresh_reports_cb = refresh_reports_cb  # 🔥 IMPORTANT

        # ---------- STYLE ----------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=CARD_BG,
            foreground=TEXT_LIGHT,
            fieldbackground=CARD_BG,
            rowheight=28,
            font=("Segoe UI", 11),
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

        for col in columns:
            self.heading(col, text=col)
            self.column(col, anchor="center", width=110)

        self.row_buttons = {}
        self.refresh()

    # ======================================================
    # REFRESH LIST + REPORTS
    # ======================================================
    def refresh(self):
        self.delete(*self.get_children())
        for btn in self.row_buttons.values():
            btn.destroy()
        self.row_buttons.clear()

        for row in self.repo.fetch_transactions():
            txn_id = row[0]
            self.insert("", "end", iid=txn_id, values=row[1:8])
            self._add_remove_button(txn_id)

        # 🔥 Trigger reports refresh
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
            self.parent,
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
            self.refresh()  # auto refresh list + reports
        except Exception as e:
            messagebox.showerror("Error", str(e))
