# 💰 K Personal Expense Checker

A modern, offline **desktop expense tracking application** built using **Python & Tkinter**.  
It helps users manage income and expenses with **real-time analytics, charts, and visual indicators**.

---

## 🚀 Features

### ✅ Transaction Management
- Add **Income** and **Expense** entries
- Categories, payment methods, and tags
- Delete transactions instantly
- Month & Year based filtering

### 📊 Visual Reports & Analytics
- **Expensometer Gauge**
  - Green → Good savings
  - Grey → Moderate spending
  - Red → Overspending
- **Total Income & Expense cards**
- **3D-style Pie Chart** showing expense distribution
- **Income vs Expense Line Graph** (entire period)

### 🎨 UI & Experience
- Ferrari-inspired **dark modern theme**
- Clean dashboard layout
- Responsive resizing
- Smooth real-time updates

### 💾 Offline & Portable
- Uses **SQLite** for local storage
- Database auto-created on first run
- Works without internet
- Packaged as a **single `.exe` file**

---

## 🧰 Technology Stack

| Component | Technology |
|---------|------------|
| Language | Python 3 |
| GUI | Tkinter |
| Database | SQLite |
| Charts | Matplotlib |
| Images | Pillow (PIL) |
| Packaging | PyInstaller |

---

## 📂 Project Structure
k-expense-tracker/ │ ├── app.py ├── expenses.db            # Auto-created on first run │ ├── gui/ │   ├── main_window.py │   ├── transaction_form.py │   ├── transaction_list.py │   ├── reports.py │   └── settings.py │ ├── db/ │   ├── models.py │   └── repository.py │ ├── assets/ │   ├── exp.png             # Expensometer base │   ├── icon.ico            # App icon │   └── other images │ ├── requirements.txt └── README.md

---

## ▶️ How to Run (Python)

### 1️⃣ Create Virtual Environment

python -m venv venv
venv\Scripts\activate

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Run Application

python app.py


---

🖥️ Create EXE File

1️⃣ Install PyInstaller

pip install pyinstaller

2️⃣ Build Executable

pyinstaller --onefile --windowed --add-data "assets;assets" app.py

3️⃣ Output

dist/app.exe

> The database (expenses.db) will be created automatically wherever the EXE is run.




---

🔒 Data Handling

All data is stored locally

No cloud or internet usage

SQLite automatically creates the database file

User data remains private



---

📈 Expensometer Logic

Condition	Status

Expense > Income	Overspent 🔴
Expense < 50% Income	Moderate ⚪
High Savings	Good Savings 🟢



---

🛠️ Future Enhancements

Monthly budget limits

CSV / Excel export

Category-based analytics

Cloud sync option

Mobile version



---

👤 Author

K Sharath
Personal Expense Checker Project


---

📜 License

This project is for educational and personal use.
Feel free to modify and extend.
