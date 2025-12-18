import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, FancyArrowPatch
from db.repository import Repository
import numpy as np

# ================= THEME =================
CARD_BG = "#1c1c1c"
TEXT_LIGHT = "#ffffff"
FERRARI_RED = "#C4001A"
INCOME_COLOR = "#32CD32"   # green
EXPENSE_COLOR = "#FFA500"  # orange


class ReportsWindow(ttk.Frame):
    def __init__(self, parent, inline=False):
        self.repo = Repository()

        if not inline:
            self.window = tk.Toplevel(parent)
            self.window.title("Reports")
            self.window.geometry("1100x700")
            parent = self.window

        super().__init__(parent, style="Card.TFrame")
        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.build_dashboard()

    # ======================================================
    # PUBLIC REFRESH METHOD
    # ======================================================
    def refresh(self):
        self.build_dashboard()

    # ======================================================
    # DASHBOARD
    # ======================================================
    def build_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        total_income = self.repo.get_total("income")
        total_expense = self.repo.get_total("expense")

        # ---------- TOP ----------
        top_frame = tk.Frame(self, bg=CARD_BG)
        top_frame.pack(fill="x", pady=10)

        # Gauge
        gauge_frame = tk.Frame(top_frame, bg=CARD_BG)
        gauge_frame.pack(side="left", padx=(0, 20))
        self.create_income_expense_gauge(gauge_frame, total_income, total_expense)

        # Cards
        cards_frame = ttk.Frame(top_frame, style="Card.TFrame")
        cards_frame.pack(side="left", fill="x", expand=True)

        self.create_card(
            cards_frame, "Total Income", f"₹ {total_income:.2f}", INCOME_COLOR
        ).pack(fill="x", pady=5)

        self.create_card(
            cards_frame, "Total Expense", f"₹ {total_expense:.2f}", EXPENSE_COLOR
        ).pack(fill="x", pady=5)

        # ---------- CHARTS ----------
        charts_frame = tk.Frame(self, bg=CARD_BG)
        charts_frame.pack(fill="both", expand=True, pady=10)

        # Pie chart
        cats, vals = self.repo.get_expense_by_category()
        if cats:
            self.create_pie_chart(
                charts_frame, cats, vals, "Expenses by Category"
            ).pack(side="left", fill="both", expand=True, padx=10)

        # Line chart
        self.create_income_expense_line_chart(
            charts_frame
        ).pack(side="left", fill="both", expand=True, padx=10)

    # ======================================================
    # CARDS
    # ======================================================
    def create_card(self, parent, title, value, color):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=12)
        ttk.Label(frame, text=title, style="Card.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text=value,
            foreground=color,
            background=CARD_BG,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        return frame

    # ======================================================
    # PIE CHART
    # ======================================================
    def create_pie_chart(self, parent, categories, values, title):
        fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor(CARD_BG)

        ax.pie(
            values,
            labels=categories,
            autopct="%1.1f%%",
            textprops={"color": TEXT_LIGHT},
        )
        ax.set_title(title, color=TEXT_LIGHT)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        return canvas.get_tk_widget()

    # ======================================================
    # LINE CHART (WHITE BACKGROUND, DAY-WISE TOTALS)
    # ======================================================
    def create_income_expense_line_chart(self, parent):
        daily_data = self.repo.get_daily_income_expense()  # new repo function

        if not daily_data:
            return ttk.Label(parent, text="No data", foreground=TEXT_LIGHT, background=CARD_BG)

        dates = [d[0] for d in daily_data]
        income = [d[1] for d in daily_data]
        expense = [d[2] for d in daily_data]

        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        ax.plot(dates, income, color=INCOME_COLOR, marker="o", linewidth=2.5, label="Income")
        ax.plot(dates, expense, color=EXPENSE_COLOR, marker="o", linewidth=2.5, label="Expense")

        ax.set_title("Income vs Expense Over Time", color="black")
        ax.set_xlabel("Date", color="black")
        ax.set_ylabel("Amount", color="black")
        ax.tick_params(colors="black")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend()

        for spine in ax.spines.values():
            spine.set_color("black")

        fig.autofmt_xdate()
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        return canvas.get_tk_widget()

    # ======================================================
    # EXPENSOMETER GAUGE
    # ======================================================
    def create_income_expense_gauge(self, parent, income, expense):
        diff = income - expense
        max_val = max(income, expense, 1)

        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"aspect": "equal"})
        fig.patch.set_facecolor(CARD_BG)
        ax.axis("off")
        ax.set_xlim(-1, 1)
        ax.set_ylim(-0.3, 1.1)

        zones = [
            (0, 0.33, "grey"),
            (0.33, 0.66, "yellow"),
            (0.66, 1.0, "red"),
        ]

        for s, e, c in zones:
            ax.add_patch(Wedge((0, 0), 1, 180 - s * 180, 180 - e * 180, color=c, alpha=0.85))

        for i in range(11):
            a = np.deg2rad(180 - i * 18)
            ax.plot([0.9 * np.cos(a), np.cos(a)], [0.9 * np.sin(a), np.sin(a)], lw=2)

        ax.add_patch(Circle((0, 0), 0.05, color="black"))

        angle = 180 - ((diff + max_val) / (2 * max_val)) * 180
        ax.add_patch(
            FancyArrowPatch(
                (0, 0),
                (0.8 * np.cos(np.deg2rad(angle)), 0.8 * np.sin(np.deg2rad(angle))),
                mutation_scale=25,
                lw=3,
                color="black",
            )
        )

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack()

        tk.Label(
            parent,
            text="EXPENSOMETER",
            bg="white",
            fg="black",
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(5, 0))

        if diff >= max_val * 0.66:
            txt, clr = "Potential for accident", "red"
        elif diff >= max_val * 0.33:
            txt, clr = "Don’t hit the accelerator too much", "orange"
        else:
            txt, clr = "Good speed", "green"

        tk.Label(
            parent,
            text=txt,
            fg=clr,
            bg=CARD_BG,
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(2, 10))
