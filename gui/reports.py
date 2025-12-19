import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from db.repository import Repository
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import os
import math

# ================= THEME =================
CARD_BG = "#1c1c1c"
TEXT_LIGHT = "#ffffff"
FERRARI_RED = "#C4001A"
INCOME_COLOR = "#32CD32"
EXPENSE_COLOR = "#FFA500"


class ReportsWindow(ttk.Frame):
    def __init__(self, parent, inline=False):
        super().__init__(parent)

        self.repo = Repository()
        self.month = "All"

        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_dashboard()

    # ======================================================
    # PUBLIC API
    # ======================================================
    def set_filters(self, month):
        self.month = month
        self.refresh()

    def refresh(self):
        self.build_dashboard()

    # ======================================================
    # DASHBOARD
    # ======================================================
    def build_dashboard(self):
        for w in self.winfo_children():
            w.destroy()

        total_income = self.repo.get_total("income", self.month)
        total_expense = self.repo.get_total("expense", self.month)

        # ---------- TOP ----------
        top = tk.Frame(self, bg=CARD_BG)
        top.pack(fill="x", pady=10)

        gauge_frame = tk.Frame(top, bg=CARD_BG)
        gauge_frame.pack(side="left", padx=20)
        self.create_gauge(gauge_frame, total_income, total_expense)

        cards = tk.Frame(top, bg=CARD_BG)
        cards.pack(side="left", fill="x", expand=True)

        self.create_card(cards, "Total Income", f"₹ {total_income:.2f}", INCOME_COLOR)
        self.create_card(cards, "Total Expense", f"₹ {total_expense:.2f}", EXPENSE_COLOR)

        # ---------- CHARTS ----------
        charts = tk.Frame(self, bg=CARD_BG)
        charts.pack(fill="both", expand=True, pady=10)

        cats, vals = self.repo.get_expense_by_category(self.month)
        self.create_pie_chart(charts, cats, vals, "Expenses by Category").pack(
            side="left", expand=True
        )

        self.create_line_chart(charts).pack(side="left", expand=True)

    # ======================================================
    # CARD
    # ======================================================
    def create_card(self, parent, title, value, color):
        frame = tk.Frame(parent, bg=CARD_BG)
        frame.pack(fill="x", pady=6)

        tk.Label(frame, text=title, fg=TEXT_LIGHT, bg=CARD_BG, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(
            frame,
            text=value,
            fg=color,
            bg=CARD_BG,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

    # ======================================================
    # PIE CHART (3D MODERN STYLE)
    # ======================================================
    def create_pie_chart(self, parent, categories, values, title):
        fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=100)
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor(CARD_BG)
        ax.axis('equal')  # Make circular

        if not values or sum(values) == 0:
            wedges, texts = ax.pie(
                [1], labels=["No data"], colors=["#555555"], startangle=90,
                wedgeprops=dict(width=0.6, edgecolor=CARD_BG)
            )
            for t in texts:
                t.set_color("white")
                t.set_fontsize(10)
        else:
            colors = plt.cm.Set3.colors  # pastel modern palette
            wedges, texts, autotexts = ax.pie(
                values,
                labels=categories,
                autopct="%1.1f%%",
                startangle=90,
                pctdistance=0.75,
                wedgeprops=dict(width=0.6, edgecolor=CARD_BG, linewidth=1),
                colors=colors
            )
            # Category labels in white
            for t in texts:
                t.set_color("white")
                t.set_fontsize(9)
            # Percentages in black
            for at in autotexts:
                at.set_color("black")
                at.set_fontsize(9)
                at.set_fontweight("bold")

        ax.set_title(title, color=TEXT_LIGHT, fontsize=11, pad=10)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        return canvas.get_tk_widget()

    # ======================================================
    # LINE CHART (INCOME VS EXPENSE WHOLE PERIOD)
    # ======================================================
    def create_line_chart(self, parent):
        data = self.repo.fetch_transactions()  # All transactions

        if not data:
            return tk.Label(parent, text="No data", fg=TEXT_LIGHT, bg=CARD_BG, font=("Segoe UI", 11))

        # Aggregate income and expense per day
        daily_totals = {}
        for row in data:
            date_str = row[1]  # Date
            amount = float(row[2])  # Amount
            txn_type = row[3].lower()  # Type

            if date_str not in daily_totals:
                daily_totals[date_str] = {'income': 0, 'expense': 0}

            if txn_type == "income":
                daily_totals[date_str]['income'] += amount
            elif txn_type == "expense":
                daily_totals[date_str]['expense'] += amount

        sorted_dates = sorted(daily_totals.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
        dates, income, expense = [], [], []
        for d in sorted_dates:
            dates.append(d)
            income.append(daily_totals[d]['income'])
            expense.append(daily_totals[d]['expense'])

        # Plot graph
        fig, ax = plt.subplots(figsize=(4.5, 3.5), dpi=100)
        ax.plot(dates, income, label="Income", color=INCOME_COLOR, marker="o")
        ax.plot(dates, expense, label="Expense", color=EXPENSE_COLOR, marker="o")

        ax.set_title("Income vs Expense (All Period)", color=TEXT_LIGHT, fontsize=11)
        ax.tick_params(axis='x', labelrotation=20, labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        ax.legend(fontsize=9)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        return canvas.get_tk_widget()

    # ======================================================
    # EXPENSOMETER GAUGE (THICK BLACK NEEDLE)
    # ======================================================
    def create_gauge(self, parent, income, expense):
        img_path = os.path.join("assets", "exp.png")
        if not os.path.exists(img_path):
            return

        base = Image.open(img_path).convert("RGBA").resize((220, 220))
        size = base.size
        center = (size[0] // 2, size[1] // 2)
        radius = 90  # Needle length

        diff = income - expense
        if diff < 0:
            angle, label, color = 180, "Overspent", "red"
        elif diff < income * 0.5:
            angle, label, color = 90, "Moderate", "grey"
        else:
            angle, label, color = 0, "Good savings", "green"

        overlay = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Thick black needle
        rad = math.radians(180 - angle)
        tip = (center[0] + radius * math.cos(rad),
               center[1] - radius * math.sin(rad))
        draw.line([center, tip], fill="black", width=6)

        img = ImageTk.PhotoImage(Image.alpha_composite(base, overlay))

        lbl = tk.Label(parent, image=img, bg=CARD_BG)
        lbl.image = img
        lbl.pack()
        tk.Label(parent, text=label, fg=color, bg=CARD_BG, font=("Segoe UI", 13, "bold")).pack()
