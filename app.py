from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras
from config import SUPABASE_URL

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Biar gak error di background thread VS Code
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

app = Flask(__name__)
app.secret_key = "rahasia_flask_edward"

# ==========================================
# KONEKSI DATABASE SUPABASE
# ==========================================
def get_db_connection():
    conn = psycopg2.connect(SUPABASE_URL)
    return conn

# ==========================================
# HALAMAN UTAMA - READ DATA
# ==========================================
@app.route("/")
def index():
    conn = get_db_connection()
    # Pake RealDictCursor biar hasilnya mirip dictionary kayak di MySQL
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute("SELECT * FROM pelanggan ORDER BY id DESC")
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("index.html", data=data)

# ==========================================
# CREATE DATA
# ==========================================
@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "POST":
        nama = request.form["nama"]
        umur = request.form["umur"]
        skor_pelayanan = request.form["skor_pelayanan"]
        skor_kualitas = request.form["skor_kualitas"]
        waktu_tunggu = request.form["waktu_tunggu"]
        status = request.form["status"]

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # PostgreSQL tetap pakai %s
        sql = """
        INSERT INTO pelanggan (nama, umur, skor_pelayanan, skor_kualitas, waktu_tunggu, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (nama, umur, skor_pelayanan, skor_kualitas, waktu_tunggu, status))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Data pelanggan berhasil ditambahkan!")
        return redirect(url_for("index"))

    return render_template("tambah.html")

# ==========================================
# DELETE DATA (Contoh aja, Edit menyesuaikan)
# ==========================================
@app.route("/hapus/<int:id>")
def hapus(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pelanggan WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Data berhasil dihapus!")
    return redirect(url_for("index"))

# ==========================================
# GENERATE 1000 DATA SIMULASI
# ==========================================
@app.route("/generate-data")
def generate_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    np.random.seed(42)

    data_simulasi = []
    for i in range(1000):
        nama = f"Pelanggan {i+1}"
        umur = np.random.randint(18, 60)
        skor_pelayanan = round(np.random.uniform(40, 100), 2)
        skor_kualitas = round(np.random.uniform(40, 100), 2)
        waktu_tunggu = round(np.random.uniform(5, 60), 2) # Dalam menit

        # Logika: Puas jika pelayanan dan kualitas di atas 70, dan antre kurang dari 25 menit
        if skor_pelayanan >= 70 and skor_kualitas >= 70 and waktu_tunggu <= 25:
            status = "Puas"
        else:
            status = "Tidak Puas"

        data_simulasi.append((nama, umur, skor_pelayanan, skor_kualitas, waktu_tunggu, status))

    sql = """
    INSERT INTO pelanggan (nama, umur, skor_pelayanan, skor_kualitas, waktu_tunggu, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    # execute_batch lebih efisien di psycopg2 dibanding executemany
    psycopg2.extras.execute_batch(cursor, sql, data_simulasi)
    
    conn.commit()
    cursor.close()
    conn.close()

    flash("1000 data simulasi pelanggan berhasil dibuat!")
    return redirect(url_for("index"))

# ==========================================
# AMBIL DATA KE PANDAS
# ==========================================
def get_dataframe():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM pelanggan", conn)
    conn.close()
    return df

# ==========================================
# VISUALISASI DATA
# ==========================================
@app.route("/visualisasi")
def visualisasi():
    df = get_dataframe()

    # Bar Chart
    plt.figure(figsize=(8, 5))
    status_count = df["status"].value_counts()
    status_count.plot(kind="bar", color=['#ff9999','#66b3ff'])
    plt.title("Jumlah Pelanggan Berdasarkan Kepuasan")
    plt.tight_layout()
    plt.savefig("static/charts/bar.png")
    plt.close()

    # Pie Chart
    plt.figure(figsize=(7, 7))
    status_count.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Persentase Kepuasan Pelanggan")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("static/charts/pie.png")
    plt.close()

    return render_template("visualisasi.html", total=len(df))

# ==========================================
# MACHINE LEARNING (RF vs DT)
# ==========================================
@app.route("/machine-learning")
def machine_learning():
    df = get_dataframe()
    if len(df) < 10:
        return "Data kurang. Klik Generate Data dulu."

    X = df[["umur", "skor_pelayanan", "skor_kualitas", "waktu_tunggu"]]
    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Model 1: Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred) * 100

    # Model 2: Decision Tree
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(X_train, y_train)
    dt_pred = dt_model.predict(X_test)
    dt_acc = accuracy_score(y_test, dt_pred) * 100

    # Feature Importance dari Random Forest
    features = list(zip(X.columns, rf_model.feature_importances_))
    features.sort(key=lambda x: x[1], reverse=True)

    return render_template(
        "machine_learning.html",
        rf_acc=round(rf_acc, 2),
        dt_acc=round(dt_acc, 2),
        total_train=len(X_train),
        total_test=len(X_test),
        features=features
    )

@app.route("/prediksi", methods=["POST"])
def prediksi():
    df = get_dataframe()
    X = df[["umur", "skor_pelayanan", "skor_kualitas", "waktu_tunggu"]]
    y = df["status"]

    # Gunakan algoritma yang akurasinya biasanya lebih tinggi (RF)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    umur = float(request.form["umur"])
    skor_pelayanan = float(request.form["skor_pelayanan"])
    skor_kualitas = float(request.form["skor_kualitas"])
    waktu_tunggu = float(request.form["waktu_tunggu"])

    data_baru = pd.DataFrame([[umur, skor_pelayanan, skor_kualitas, waktu_tunggu]], 
                             columns=["umur", "skor_pelayanan", "skor_kualitas", "waktu_tunggu"])

    hasil = model.predict(data_baru)[0]

    return render_template("machine_learning.html", hasil=hasil)

if __name__ == "__main__":
    app.run(debug=True)