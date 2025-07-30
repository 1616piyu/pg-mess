# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import os

DB = 'data.db'

# ------------------ Auto DB Setup ------------------
def initialize_db():
    if not os.path.exists(DB):
        con = sqlite3.connect(DB)
        cur = con.cursor()

        # Create tables
        cur.execute('''
            CREATE TABLE IF NOT EXISTS menu_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                food_items TEXT NOT NULL
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                rating INTEGER,
                comment TEXT
            )
        ''')

        # Add sample data if empty
        sample_data = [
            ('Monday', 'Breakfast', 'Poha & Tea'),
            ('Monday', 'Lunch', 'Dal, Rice, Roti'),
            ('Monday', 'Dinner', 'Paneer & Rice'),
            ('Tuesday', 'Breakfast', 'Idli & Sambar'),
            ('Tuesday', 'Lunch', 'Rajma Chawal'),
            ('Tuesday', 'Dinner', 'Chole Bhature')
        ]
        cur.executemany("INSERT INTO menu_schedule (day, meal_type, food_items) VALUES (?, ?, ?)", sample_data)

        con.commit()
        con.close()
        print("✅ Database created with sample menu.")

        app = Flask(__name__)
app.secret_key = 'mlv_pg_secret'

initialize_db()  # 🟢 This line must be here


# ------------------ Helper Function ------------------
def get_today_menu():
    today = datetime.now().strftime('%A')
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT meal_type, food_items FROM menu_schedule WHERE day = ?", (today,))
    data = cur.fetchall()
    con.close()

    menu = {'Breakfast': '', 'Lunch': '', 'Dinner': ''}
    for meal_type, food in data:
        menu[meal_type] = food
    return menu

# ------------------ Routes ------------------
@app.route('/')
def home():
    try:
        menu = get_today_menu()
        return render_template("index.html", menu=menu)
    except Exception as e:
        return f"Error: {e}"

@app.route('/weekly')
def weekly():
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT * FROM menu_schedule")
        data = cur.fetchall()
        con.close()
        return render_template("weekly_menu.html", data=data)
    except Exception as e:
        return f"Error: {e}"

@app.route('/api/today')
def api_today():
    return jsonify(get_today_menu())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == 'admin' and pwd == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        day = request.form['day']
        meal = request.form['meal']
        food = request.form['food']
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT id FROM menu_schedule WHERE day=? AND meal_type=?", (day, meal))
        existing = cur.fetchone()
        if existing:
            cur.execute("UPDATE menu_schedule SET food_items=? WHERE day=? AND meal_type=?", (food, day, meal))
        else:
            cur.execute("INSERT INTO menu_schedule (day, meal_type, food_items) VALUES (?, ?, ?)", (day, meal, food))
        con.commit()
        con.close()
        return redirect(url_for('weekly'))
    return render_template("admin.html")

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        day = request.form['day']
        meal = request.form['meal']
        rating = int(request.form['rating'])
        comment = request.form['comment']
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("INSERT INTO feedback (day, meal_type, rating, comment) VALUES (?, ?, ?, ?)",
                    (day, meal, rating, comment))
        con.commit()
        con.close()
        return render_template("feedback_thanks.html")
    return render_template("feedback.html")

@app.route('/view-feedback')
def view_feedback():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT * FROM feedback ORDER BY id DESC")
    data = cur.fetchall()
    con.close()
    return render_template("view_feedback.html", data=data)

# ------------------ Start Server ------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
