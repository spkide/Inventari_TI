from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = "supersecret123"
DB = "database.db"

# ======================
# DB
# ======================
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
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
    """)
    conn.commit()
    conn.close()

# ======================
# DASHBOARD
# ======================
@app.route("/")
def dashboard():
    conn = get_db()
    inventario = conn.execute("SELECT * FROM inventario").fetchall()
    conn.close()
    return render_template("dashboard.html", inventario=inventario)

# ======================
# TABLA AJAX
# ======================
@app.route("/tabla_inventario")
def tabla_inventario():
    conn = get_db()
    inventario = conn.execute("SELECT * FROM inventario").fetchall()
    conn.close()
    return render_template("tabla_inventario.html", inventario=inventario)

# ======================
# ADD
# ======================
@app.route("/add", methods=["POST"])
def add():
    f = request.form
    conn = get_db()
    conn.execute("""
        INSERT INTO inventario
        (nombre_usuario, correo_usuario, usuario_servidor, servidor, carpetas,
         equipo, marca, modelo, numero_serie, numero_economico, mac)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        f["nombre_usuario"],
        f["correo_usuario"],
        f["usuario_servidor"],
        f["servidor"],
        f["carpetas"],
        f["equipo"],
        f["marca"],
        f["modelo"],
        f["numero_serie"],
        f["numero_economico"],
        f["mac"]
    ))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ======================
# EXPORT EXCEL
# ======================
@app.route("/export_excel")
def export_excel():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM inventario", conn)
    conn.close()

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name="inventario.xlsx",
        as_attachment=True
    )

# ======================
# EXPORT PDF (DUMMY para que no truene)
# ======================
@app.route("/export_pdf")
def export_pdf():
    return "PDF pendiente, pero ya no truena 😎"

# ======================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
