from db.models import get_connection


class Repository:
    # ======================================================
    # ADD TRANSACTION
    # ======================================================
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

    # ======================================================
    # FETCH ALL TRANSACTIONS (LIST VIEW)
    # ======================================================
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

    # ======================================================
    # TOTAL INCOME / EXPENSE (MONTH FILTER ONLY)
    # ======================================================
    def get_total(self, txn_type, month="All"):
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT SUM(amount)
            FROM transactions
            WHERE type = ?
        """
        params = [txn_type]

        if month != "All":
            query += " AND strftime('%m', date) = ?"
            params.append(month.zfill(2))

        cur.execute(query, params)
        total = cur.fetchone()[0] or 0

        conn.close()
        return total

    # ======================================================
    # EXPENSE BY CATEGORY (MONTH FILTER ONLY)
    # ======================================================
    def get_expense_by_category(self, month="All"):
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT category, SUM(amount)
            FROM transactions
            WHERE type = 'expense'
        """
        params = []

        if month != "All":
            query += " AND strftime('%m', date) = ?"
            params.append(month.zfill(2))

        query += " GROUP BY category"

        cur.execute(query, params)
        rows = cur.fetchall()

        conn.close()
        return [r[0] for r in rows], [r[1] for r in rows]

    # ======================================================
    # DAILY AGGREGATED DATA (LINE CHART – MONTH FILTER ONLY)
    # ======================================================
    def fetch_transactions_filtered(self, month="All"):
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                date,
                SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS income,
                SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expense
            FROM transactions
        """
        params = []

        if month != "All":
            query += " WHERE strftime('%m', date) = ?"
            params.append(month.zfill(2))

        query += " GROUP BY date ORDER BY date"

        cur.execute(query, params)
        rows = cur.fetchall()

        conn.close()
        return rows

    # ======================================================
    # DELETE TRANSACTION
    # ======================================================
    def delete_transaction(self, txn_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        conn.commit()
        conn.close()
