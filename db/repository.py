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
            SELECT id, date, amount, type, category, payment_method, tags
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
    
