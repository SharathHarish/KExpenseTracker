from db.models import get_connection
from datetime import datetime

class Repository:
    def add_transaction(self, data):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO transactions
            (date, amount, type, category, payment_method, tags)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            data,
        )

        conn.commit()
        conn.close()

    def fetch_transactions(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, date, amount, type, category, payment_method, tags, note
            FROM transactions
            ORDER BY date DESC
            """
        )

        rows = cur.fetchall()
        conn.close()
        return rows

    def get_total(self, txn_type):
        """Return total income or total expense"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = ?", (txn_type,)
        )
        total = cur.fetchone()[0] or 0
        conn.close()
        return total

    def get_expense_by_category(self):
        """Return expense totals by category"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT category, SUM(amount) 
            FROM transactions 
            WHERE type='expense'
            GROUP BY category
            """
        )
        rows = cur.fetchall()
        conn.close()
        categories = [row[0] for row in rows]
        values = [row[1] for row in rows]
        return categories, values

    def get_income_by_category(self):
        """Return income totals by category"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT category, SUM(amount) 
            FROM transactions 
            WHERE type='income'
            GROUP BY category
            """
        )
        rows = cur.fetchall()
        conn.close()
        categories = [row[0] for row in rows]
        values = [row[1] for row in rows]
        return categories, values

    def delete_transaction(self, txn_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        conn.commit()
        conn.close()
    def get_daily_income_expense(self):
        """
        Returns a list of tuples: (date, total_income, total_expense)
        Dates are in datetime.date format
        """
        query = "SELECT date, type, SUM(amount) as total FROM transactions GROUP BY date, type ORDER BY date ASC"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        daily = {}
        for row in rows:
            try:
                # Support multiple formats
                for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                    try:
                        date = datetime.strptime(row["date"], fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                continue

            if date not in daily:
                daily[date] = {"income": 0, "expense": 0}

            txn_type = row["type"].lower()
            amount = float(row["total"])
            if txn_type == "income":
                daily[date]["income"] = amount
            elif txn_type == "expense":
                daily[date]["expense"] = amount

        # Convert to sorted list of tuples
        result = [(date, daily[date]["income"], daily[date]["expense"]) for date in sorted(daily)]
        return result
