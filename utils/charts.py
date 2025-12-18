from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from db.repository import Repository


def monthly_summary(parent):
    repo = Repository()
    data = repo.fetch_transactions()

    total_income = 0
    total_expense = 0

    for row in data:
        amount = row[2]
        tx_type = row[3]

        if tx_type == "income":
            total_income += amount
        elif tx_type == "expense":
            total_expense += amount

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    ax.bar(["Income", "Expense"], [total_income, total_expense])
    ax.set_title("Income vs Expense")
    ax.set_ylabel("Amount")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
