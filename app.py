from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'supersecret123'
DB = 'database.db'

# ======================
# DB
# ======================
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT,
            correo_usuario TEXT,
            usuario_servidor TEXT,
            servidor TEXT,
            carpetas TEXT,
            equipo TEXT,
            marca TEXT,
            modelo TEXT,
            numero_serie TEXT,
            numero_economico TEXT,
            mac TEXT
        )
    ''')

    conn.execute(
        'INSERT OR IGNORE INTO usuarios (username, password) VALUES (?,?)',
        ('admin', 'admin123')
    )

    conn.commit()
    conn.close()

# ======================
# LOGIN
# ======================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM usuarios WHERE username=? AND password=?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Credenciales incorrectas')

    return render_template('login.html')

# ======================
# REGISTER
# ======================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO usuarios (username,password) VALUES (?,?)',
                (request.form['username'], request.form['password'])
            )
            conn.commit()
            return redirect(url_for('login'))
        except:
            return render_template('register.html', error='Usuario ya existe')
        finally:
            conn.close()

    return render_template('register.html')

# ======================
# DASHBOARD
# ======================
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    inventario = conn.execute('SELECT * FROM inventario').fetchall()
    conn.close()

    return render_template('dashboard.html', inventario=inventario)

# ======================
# ADD
# ======================
@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect(url_for('login'))

    f = request.form
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO inventario (
            nombre_usuario, correo_usuario, usuario_servidor, servidor,
            carpetas, equipo, marca, modelo,
            numero_serie, numero_economico, mac
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        f['nombre_usuario'],
        f['correo_usuario'],
        f['usuario_servidor'],
        f['servidor'],
        f['carpetas'],
        f['equipo'],
        f['marca'],
        f['modelo'],
        f['numero_serie'],
        f['numero_economico'],
        f['mac']
    ))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# ======================
# EDIT
# ======================
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        f = request.form
        conn.execute('''
            UPDATE inventario SET
            nombre_usuario=?,
            correo_usuario=?,
            usuario_servidor=?,
            servidor=?,
            carpetas=?,
            equipo=?,
            marca=?,
            modelo=?,
            numero_serie=?,
            numero_economico=?,
            mac=?
            WHERE id=?
        ''', (
            f['nombre_usuario'],
            f['correo_usuario'],
            f['usuario_servidor'],
            f['servidor'],
            f['carpetas'],
            f['equipo'],
            f['marca'],
            f['modelo'],
            f['numero_serie'],
            f['numero_economico'],
            f['mac'],
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    item = conn.execute(
        'SELECT * FROM inventario WHERE id=?', (id,)
    ).fetchone()
    conn.close()

    return render_template('edit.html', item=item)

# ======================
# DELETE
# ======================
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM inventario WHERE id=?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# ======================
# EXPORT EXCEL
# ======================
@app.route('/export/excel')
def export_excel():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM inventario', conn)
    conn.close()

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(output, download_name='inventario.xlsx', as_attachment=True)

# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ======================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
