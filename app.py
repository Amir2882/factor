from flask import Flask, render_template, request, redirect, url_for, send_file, make_response, session
import sqlite3
import pdfkit
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # برای session

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return 'نام کاربری یا رمز عبور اشتباه است'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    sales = conn.execute('SELECT * FROM sales').fetchall()
    conn.close()
    return render_template('index.html', sales=sales)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.form
        weight = float(data['weight'])
        price_per_kg = float(data['price_per_kg'])
        total_price = weight * price_per_kg
        scale_cost = float(data['scale_cost'])
        net_price = total_price - scale_cost

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO sales (date, fruit_type, weight, price_per_kg, total_price,
                               cold_storage_name, scale_cost, net_price,
                               car_plate, driver_name, box_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['date'],
            data['fruit_type'],
            weight,
            price_per_kg,
            total_price,
            data['cold_storage_name'],
            scale_cost,
            net_price,
            data['car_plate'],
            data['driver_name'],
            data['box_count']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_fruit.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    sale = conn.execute('SELECT * FROM sales WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        data = request.form
        weight = float(data['weight'])
        price_per_kg = float(data['price_per_kg'])
        total_price = weight * price_per_kg
        scale_cost = float(data['scale_cost'])
        net_price = total_price - scale_cost

        conn.execute('''
            UPDATE sales SET date=?, fruit_type=?, weight=?, price_per_kg=?,
            total_price=?, cold_storage_name=?, scale_cost=?, net_price=?,
            car_plate=?, driver_name=?, box_count=?
            WHERE id=?
        ''', (
            data['date'],
            data['fruit_type'],
            weight,
            price_per_kg,
            total_price,
            data['cold_storage_name'],
            scale_cost,
            net_price,
            data['car_plate'],
            data['driver_name'],
            data['box_count'],
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit_fruit.html', sale=sale)

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM sales WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/filter', methods=['POST'])
def filter_by_date():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    start = request.form['start_date']
    end = request.form['end_date']
    conn = get_db_connection()
    sales = conn.execute("SELECT * FROM sales WHERE date BETWEEN ? AND ?", (start, end)).fetchall()
    conn.close()
    return render_template('index.html', sales=sales)

@app.route('/download/pdf')
def download_pdf():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    sales = conn.execute('SELECT * FROM sales').fetchall()
    conn.close()
    rendered = render_template('pdf_template.html', sales=sales)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=factors.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
