from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import sqlite3
import pandas as pd
from io import BytesIO
import pdfkit

app = Flask(__name__)
app.secret_key = 'supersecret123'
DB = 'database.db'

# ----------------------
# DB
# ----------------------
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS inventario(
            id INTEGER PRIMARY KEY,
            nombre_usuario TEXT,
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
        'INSERT OR IGNORE INTO usuarios(username,password) VALUES (?,?)',
        ('admin','admin123')
    )
    conn.commit()
    conn.close()

# ----------------------
# Login
# ----------------------
@app.route('/', methods=['GET','POST'])
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
            flash(f'¡Bienvenido, {username}!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('login.html', error="Usuario o contraseña incorrectos")

    return render_template('login.html')

# ----------------------
# Registro
# ----------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO usuarios(username,password) VALUES (?,?)',
                (username, password)
            )
            conn.commit()
            flash('Usuario creado correctamente', 'success')
            return redirect(url_for('login'))
        except:
            return render_template('register.html', error="Usuario ya existe")
        finally:
            conn.close()

    return render_template('register.html')

# ----------------------
# Dashboard
# ----------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    inventario = conn.execute('SELECT * FROM inventario').fetchall()
    conn.close()

    return render_template('dashboard.html', inventario=inventario)

# ----------------------
# Agregar inventario
# ----------------------
@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = request.form
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO inventario
        (nombre_usuario,usuario_servidor,servidor,carpetas,equipo,marca,modelo,
         numero_serie,numero_economico,mac)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    ''', (
        data['nombre_usuario'],
        data['usuario_servidor'],
        data['servidor'],
        data['carpetas'],
        data['equipo'],
        data['marca'],
        data['modelo'],
        data['numero_serie'],
        data['numero_economico'],
        data['mac']
    ))
    conn.commit()
    conn.close()

    flash('Inventario agregado correctamente', 'success')
    return redirect(url_for('dashboard'))

# ----------------------
# EDITAR
# ----------------------
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        data = request.form
        conn.execute('''
            UPDATE inventario SET
            nombre_usuario=?,
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
            data['nombre_usuario'],
            data['usuario_servidor'],
            data['servidor'],
            data['carpetas'],
            data['equipo'],
            data['marca'],
            data['modelo'],
            data['numero_serie'],
            data['numero_economico'],
            data['mac'],
            id
        ))
        conn.commit()
        conn.close()
        flash('Registro actualizado', 'success')
        return redirect(url_for('dashboard'))

    item = conn.execute(
        'SELECT * FROM inventario WHERE id=?',
        (id,)
    ).fetchone()
    conn.close()

    return render_template('edit.html', item=item)

# ----------------------
# ELIMINAR
# ----------------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM inventario WHERE id=?', (id,))
    conn.commit()
    conn.close()

    flash('Registro eliminado', 'success')
    return redirect(url_for('dashboard'))

# ----------------------
# Exportar Excel
# ----------------------
@app.route('/export/excel')
def export_excel():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM inventario", conn)
    conn.close()

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(output, download_name="inventario.xlsx", as_attachment=True)

# ----------------------
# Logout
# ----------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
