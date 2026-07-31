## Runing Code

```bash

# 1. Membuat virtual environment baru
python3 -m venv .venv

# 2. Mengaktifkan virtual environment
source .venv/bin/activate      # Untuk Linux/macOS
.venv\Scripts\activate         # Untuk Windows

# 3. Menginstal semua dependensi yang dibutuhkan
pip install -r requirements.txt

# 4. Menjalankan program utama
python3 main.py

# 5. Menjalankan semua unit test yang ada di folder 'tests'
python3 -m pytest tests

# 6. Menjalankan coverage test untuk melihat seberapa banyak kode yang diuji
coverage run -m pytest tests

# 7. Melihat ringkasan laporan hasil coverage
coverage report
