# 📊 Dashboard Analisis & Prediksi Kepuasan Pelanggan

Proyek ini adalah tugas mata kuliah Analisis dan Visualisasi Data (Anvisdat). Aplikasi ini merupakan *dashboard* web berbasis **Flask** dan **Supabase (PostgreSQL)** yang berfungsi untuk mengelola data pelanggan, menampilkan visualisasi data, serta memprediksi tingkat kepuasan pelanggan menggunakan algoritma *Machine Learning*.

## 🚀 Fitur Utama
- **CRUD Data Pelanggan**: Tambah, tampilkan, edit, dan hapus data skor pelanggan secara *real-time*.
- **Data Generator**: Fitur untuk men-*generate* 1.000 data simulasi pelanggan (Umur, Skor Pelayanan, Skor Kualitas, Waktu Tunggu) secara otomatis.
- **Visualisasi Data**: Menampilkan *Bar Chart* dan *Pie Chart* dari distribusi status kepuasan pelanggan menggunakan Matplotlib.
- **Machine Learning**: 
  - Komparasi akurasi antara algoritma **Random Forest** dan **Decision Tree**.
  - Menampilkan *Feature Importance* (tingkat pengaruh variabel).
  - Prediksi status pelanggan baru (Puas / Tidak Puas) berdasarkan input parameter.

## 🛠️ Teknologi yang Digunakan
- **Backend**: Python, Flask
- **Database**: PostgreSQL (via Supabase) & `psycopg2-binary`
- **Data Processing & ML**: Pandas, NumPy, Scikit-Learn
- **Visualisasi**: Matplotlib
- **Frontend**: HTML5, Bootstrap 5

## ⚙️ Cara Menjalankan Aplikasi Lokal
1. *Clone repository* ini:
   ```bash
   git clone [https://github.com/USERNAME_GITHUB_LU/flask-anvisdat-kepuasan.git](https://github.com/USERNAME_GITHUB_LU/flask-anvisdat-kepuasan.git)