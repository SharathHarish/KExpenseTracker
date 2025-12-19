# gui/reports.py
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from db.repository import Repository
from PIL import Image, ImageTk, ImageDraw
import os
import math
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
    # LINE CHART
    # ======================================================
    def create_income_expense_line_chart(self, parent):
        daily_data = self.repo.fetch_transactions()
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
    # EXPENSOMETER IMAGE + 3D DYNAMIC NEEDLE
    # ======================================================
    def create_income_expense_gauge(self, parent, total_income, total_expense):
        img_path = os.path.join("assets", "exp.png")
        if not os.path.exists(img_path):
            tk.Label(parent, text="Expensometer image not found!", bg=CARD_BG, fg="red").pack()
            return

        # Smaller gauge
        base_img = Image.open(img_path).convert("RGBA")
        base_img = base_img.resize((180, 180), Image.Resampling.LANCZOS)
        size = base_img.size
        center = (size[0] // 2, size[1] // 2)
        radius = min(center) * 0.7

        # Diff calculation
        diff = total_income - total_expense

        # Determine zone based on logic
        if diff < 0:
            zone_txt, zone_clr = "Overspent", "red"
            target_angle = 180  # right
        elif diff < 0.5 * total_income:
            zone_txt, zone_clr = "Moderate", "grey"
            target_angle = 90  # center
        else:
            zone_txt, zone_clr = "Good savings", "green"
            target_angle = 0  # left

        # Tkinter label for gauge
        needle_label = tk.Label(parent, bg=CARD_BG)
        needle_label.pack()

        # Draw needle as triangle
        def draw_needle(angle):
            overlay = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            # Flip angle: 0°=left, 180°=right
            rad = math.radians(180 - angle)
            tip_x = center[0] + radius * math.cos(rad)
            tip_y = center[1] - radius * math.sin(rad)
            width = radius * 0.05
            left_x = center[0] - width * math.sin(rad)
            left_y = center[1] - width * math.cos(rad)
            right_x = center[0] + width * math.sin(rad)
            right_y = center[1] + width * math.cos(rad)
            points = [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]
            draw.polygon(points, fill="black")
            combined = Image.alpha_composite(base_img, overlay)
            img_tk = ImageTk.PhotoImage(combined)
            needle_label.configure(image=img_tk)
            needle_label.image = img_tk

        # Animate needle smoothly
        current_angle = 180  # start from right-most (red)
        step = -2 if target_angle < current_angle else 2

        def animate():
            nonlocal current_angle
            if (step > 0 and current_angle < target_angle) or (step < 0 and current_angle > target_angle):
                current_angle += step
                if (step > 0 and current_angle > target_angle) or (step < 0 and current_angle < target_angle):
                    current_angle = target_angle
                draw_needle(current_angle)
                parent.after(15, animate)
            else:
                draw_needle(target_angle)

        animate()

        # Labels below gauge
        tk.Label(
            parent,
            text="EXPENSOMETER",
            bg=CARD_BG,
            fg=TEXT_LIGHT,
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(5, 0))

        tk.Label(
            parent,
            text=zone_txt,
            fg=zone_clr,
            bg=CARD_BG,
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(2, 10))
